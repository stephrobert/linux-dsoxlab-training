"""Configuration pytest globale pour le repo linux-training.

Expose une fonction helper ``lab_host(name)`` qui construit une connexion
testinfra avec backend ``ssh://`` et chemin de clé absolu. La liste des
hôtes (FQDN → IP) est lue dynamiquement depuis ``meta.yml`` à la racine
— pas de doublon à maintenir vs l'infra.

Usage typique dans un test pytest+testinfra ::

    from conftest import lab_host
    import pytest

    @pytest.fixture(scope="module")
    def host():
        return lab_host("alma-rhcsa-1.lab")

    def test_demo(host):
        assert host.service("demo").is_running

Fournit aussi une fixture autouse ``_apply_lab_state`` qui exécute le
``solution.sh`` du challenge sur la VM cible avant les tests, pour que
les labs passent indépendamment de l'ordre d'exécution.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest
import testinfra
import yaml

REPO_ROOT = Path(__file__).parent.resolve()
SSH_KEY = REPO_ROOT / "ssh" / "id_ed25519"
META_YML = REPO_ROOT / "meta.yml"

# Rendre le repo importable (pour scripts utilitaires éventuels)
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _build_inventory_cached() -> tuple[dict, Path | None]:
    """Construit l'inventory Ansible + un ssh_config OpenSSH une fois
    pour toute la session pytest.

    Délègue à dsoxlab.infra.inventory pour cohérence avec dsoxlab
    provision/status/ssh — même résolution IPs et même ProxyCommand
    bastion. Le ssh_config est consommé par testinfra (cf. lab_host)
    via ``ssh://<host>?ssh_config=...``, plus fiable que de bourrer
    ``ssh_extra_args`` dans une URL (espaces et quotes du ProxyCommand
    cassent le parser, d'où "Connection to UNKNOWN port 65535").

    L'inventaire ne sert qu'aux labs ``runtime: vm``. Un lab ``shell`` se
    joue sur le poste, sans la moindre VM : il ne doit donc jamais échouer
    parce que l'infra n'est pas provisionnée, ni parce qu'aucun provider
    n'a encore été choisi. Toute erreur est donc rattrapée ici et rend un
    inventaire vide ; ce sont les labs ``vm`` qui échoueront plus tard,
    dans ``lab_host()``, avec un message qui dit quoi faire.
    """
    empty = {"all": {"children": {"labenv": {"hosts": {}}}}}
    try:
        from dsoxlab.discovery.repo import read_repo_metadata
        from dsoxlab.infra.inventory import (
            build_inventory,
            read_terraform_outputs,
            write_ssh_config,
        )
    except ImportError:
        return empty, None

    # Volontairement large : provider non résolu (ProviderUnresolved), état
    # Terraform absent, meta.yml sans section infra, terraform introuvable...
    # Aucun de ces cas ne concerne un lab shell, et aucun ne justifie de faire
    # échouer le chargement de conftest.py pour TOUS les labs du dépôt.
    try:
        repo_meta = read_repo_metadata(REPO_ROOT)
        if repo_meta is None:
            return empty, None
        tf_outputs = read_terraform_outputs(repo_meta)
        inventory = build_inventory(repo_meta, terraform_outputs=tf_outputs)
        ssh_cfg = write_ssh_config(inventory, repo_meta)
        return inventory, ssh_cfg
    except Exception:  # noqa: BLE001 - degradation voulue, cf. docstring
        return empty, None


_INVENTORY, _SSH_CONFIG = _build_inventory_cached()
_LABENV_HOSTS: dict = _INVENTORY.get("all", {}).get("children", {}).get(
    "labenv", {}
).get("hosts", {})


def lab_host(name: str) -> testinfra.host.Host:
    """Retourne un host testinfra connecté en SSH au compte ``student``.

    Source de vérité : ``dsoxlab.infra.inventory.build_inventory()``,
    qui résout les IPs depuis les outputs Terraform et configure
    automatiquement ``ProxyCommand`` quand un bastion est présent
    (cas providers cloud avec subnet privé). Le ssh_config OpenSSH
    généré est consommé via ``?ssh_config=...`` plutôt que de tasser
    le ProxyCommand dans ``ssh_extra_args`` (parsing URL trop fragile
    avec espaces et guillemets).

    Args:
        name: FQDN du host tel que déclaré dans ``meta.yml: infra.hosts``
              (ex. ``alma-rhcsa-1.lab``).

    Raises:
        ValueError: si le nom n'est pas trouvé dans l'inventory.
        RuntimeError: si l'infra n'est pas provisionnée
            (``dsoxlab provision`` à lancer d'abord).
    """
    if name not in _LABENV_HOSTS:
        if not _LABENV_HOSTS:
            raise RuntimeError(
                "Aucun host dans l'inventory : as-tu lancé 'dsoxlab provision' ? "
                "Le test a besoin de l'infrastructure déployée."
            )
        raise ValueError(
            f"Host inconnu : {name}. Hôtes disponibles : {sorted(_LABENV_HOSTS)}"
        )

    if _SSH_CONFIG is None or not _SSH_CONFIG.is_file():
        raise RuntimeError(
            "ssh_config introuvable : dsoxlab non installé ou inventory vide. "
            "Lance 'dsoxlab provision' puis réessaie."
        )

    # Le User/IdentityFile/ProxyCommand vivent tous dans ssh_config.
    # On passe juste le nom du Host (alias) à testinfra.
    return testinfra.get_host(
        f"ssh://{name}?ssh_config={_SSH_CONFIG}&sudo=true"
    )


def lab_host_ip(name: str) -> str:
    """Retourne l'adresse IP d'un hôte du lab, telle que l'inventory la connaît.

    Les IP ne sont PAS déclarées dans meta.yml : Terraform les attribue (DHCP
    réservé en KVM/incus, IP privée auto dans les clouds). Un test qui code une
    adresse en dur est donc faux dès qu'on change de provider — et un sujet qui
    demande une adresse différente de celle-là coupe la notation, puisque
    testinfra se connecte via l'inventory.

    Args:
        name: FQDN de l'hôte tel que déclaré dans ``meta.yml: infra.hosts``.

    Raises:
        ValueError: si l'hôte est inconnu de l'inventory.
    """
    hote = _LABENV_HOSTS.get(name)
    if not hote or not hote.get("ansible_host"):
        raise ValueError(
            f"Pas d'IP pour {name} dans l'inventory. "
            f"Hôtes disponibles : {sorted(_LABENV_HOSTS)}"
        )
    return str(hote["ansible_host"])


def lab_target_host(default: str) -> str:
    """Retourne le FQDN de la target sur laquelle valider.

    C'est le point d'entrée des labs MULTI-DISTRIB : au lieu de coder un
    hôte en dur (ce qui rendrait une target Ubuntu déclarée mais jamais
    testée — le contrat mentirait), le test demande ici l'hôte réellement
    choisi.

    Source : ``DSOXLAB_TARGET_HOST``, exporté par ``dsoxlab check`` depuis
    la target résolue (``--target``, sinon la target de session, sinon la
    target ``default`` du lab.yaml).

    Args:
        default: FQDN à utiliser hors dsoxlab (pytest lancé à la main, CI) —
                 typiquement la target ``default`` du lab.

    Usage dans un test::

        TARGET_HOST = lab_target_host("alma-rhcsa-1.lab")
    """
    return os.environ.get("DSOXLAB_TARGET_HOST") or default


# ----------------------------------------------------------------------
# Fixture autouse : applique l'état du lab avant ses tests.
# ----------------------------------------------------------------------


def _find_lab_root(test_path: Path) -> Path | None:
    """Remonte les parents pour trouver ``labs/<category>/<section>/<lab>/``.

    Retourne le dossier ``<lab>`` (parent de ``challenge/``), ou None si
    le test n'est pas dans un lab.
    """
    labs_dir = REPO_ROOT / "labs"
    for parent in test_path.parents:
        try:
            rel = parent.relative_to(labs_dir)
        except ValueError:
            continue
        # rel doit être de la forme <category>/<section>/<lab> (3 composants)
        # ou plus profond pour les labs avec sous-sous-section
        if len(rel.parts) >= 3:
            # Le lab root est le plus profond qui contient un lab.yaml
            if (parent / "lab.yaml").is_file():
                return parent
    return None


def _run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    """Exécute une commande, lève une RuntimeError lisible en cas d'échec."""
    result = subprocess.run(cmd, capture_output=True, text=True, **kwargs)
    if result.returncode != 0:
        raise RuntimeError(
            f"Commande échouée (exit {result.returncode}) : {' '.join(cmd)}\n"
            f"--- stdout ---\n{result.stdout}\n"
            f"--- stderr ---\n{result.stderr}"
        )
    return result


def _read_lab_runtime(lab_root: Path) -> tuple[str, str | None]:
    """Lit ``lab.yaml`` et retourne ``(runtime_type, host_or_None)``."""
    lab_yaml = lab_root / "lab.yaml"
    with lab_yaml.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    runtime = data.get("runtime") or {}
    host = runtime.get("host")
    # Labs VM mono/multi-hôte : le host peut vivre dans runtime.targets[].host
    # (schéma des labs l2+). On prend la target ``default`` si déclarée, sinon
    # la première.
    if host is None:
        targets = runtime.get("targets") or []
        if targets:
            default = runtime.get("default")
            chosen = next(
                (t for t in targets if t.get("name") == default), targets[0]
            )
            host = chosen.get("host")
    return str(runtime.get("type", "shell")), host


def _replay_shell_solution(lab_root: Path, rel_path: Path) -> None:
    """Joue la solution d'un lab shell dans son workdir.

    Un lab shell n'a rien à provisionner : sa solution est un script bash joué
    dans ``challenge/work/``, exactement là où l'apprenant travaille (le
    conftest local de chaque lab y fait un chdir par test).

    Le script est chiffré ansible-vault comme les solutions VM — l'apprenant ne
    doit pas pouvoir le lire dans le dépôt. On le déchiffre en mémoire, jamais
    sur disque.

    Solution absente → no-op : les tests tournent sur l'état du workdir tel
    quel, ce qui reste le comportement voulu en ``dsoxlab check``.
    """
    solution_sh = REPO_ROOT / "solution" / rel_path / "solution.sh"
    if not solution_sh.is_file():
        return

    script = solution_sh.read_text()
    if script.lstrip().startswith("$ANSIBLE_VAULT"):
        vault_pass = REPO_ROOT / ".vault-pass"
        if not vault_pass.is_file():
            pytest.skip(
                f"[{lab_root.name}] solution.sh chiffrée mais .vault-pass "
                "absent : impossible de la rejouer."
            )
        # _run impose capture_output/text et lève si la commande échoue.
        script = _run([
            "ansible-vault", "view", str(solution_sh),
            "--vault-password-file", str(vault_pass),
        ]).stdout

    workdir = lab_root / "challenge" / "work"
    workdir.mkdir(parents=True, exist_ok=True)
    # subprocess.run direct (pas _run) : on veut le script sur stdin et un
    # message d'erreur qui nomme le lab. bash -e arrête la solution au premier
    # échec — sinon un test pourrait passer alors qu'une étape a silencieusement
    # échoué, et la solution "prouverait" un test qu'elle n'honore pas.
    res = subprocess.run(
        ["bash", "-e"],
        input=script,
        cwd=workdir,
        capture_output=True,
        text=True,
        check=False,
    )
    if res.returncode != 0:
        raise RuntimeError(
            f"solution.sh a échoué pour {lab_root.name} "
            f"(rc={res.returncode}).\n{res.stdout}\n{res.stderr}"
        )


@pytest.fixture(scope="module", autouse=True)
def _apply_lab_state(request) -> None:
    """Applique la solution officielle du formateur avant les tests.

    Cette fixture sert à la **validation CI** (rejouer la solution
    officielle pour vérifier que les tests passent). Pour la validation
    apprenant via ``dsoxlab check`` qui teste l'état actuel de la VM,
    désactiver via ``LAB_NO_REPLAY=1``.

    Comportement :

    - ``runtime: vm`` (et alias kvm/incus) → joue
      ``solution/<category>/<chemin-relatif-du-lab>/solution.yaml``
      via ansible-runner sur la target par défaut. Si le fichier est
      chiffré ansible-vault, lit ``.vault-pass`` à la racine.
    - ``runtime: shell`` → no-op (l'apprenant a fait ses commandes
      en local, on teste l'état du workdir tel quel).
    - Solution absente → log + skip soft (les tests tournent quand même
      sur l'état actuel, mais peuvent échouer si rien n'a été fait).
    """
    if os.environ.get("LAB_NO_REPLAY") == "1":
        return

    test_path = Path(str(request.fspath)).resolve()
    lab_root = _find_lab_root(test_path)
    if lab_root is None:
        return  # test hors d'un lab

    runtime_type, host_name = _read_lab_runtime(lab_root)

    # Labs multi-distrib : la solution doit se rejouer sur la MÊME target que
    # celle où portent les tests, sinon on validerait un hôte et on
    # provisionnerait l'autre.
    host_name = lab_target_host(host_name) if host_name else os.environ.get(
        "DSOXLAB_TARGET_HOST"
    )

    rel_path = lab_root.relative_to(REPO_ROOT / "labs")

    # Atelier shell-local : la solution est un SCRIPT joué dans le workdir.
    # Ansible ne sert à rien ici (rien à provisionner, tout est local), mais
    # une solution reste indispensable : sans elle, les tests d'un lab shell ne
    # sont JAMAIS prouvés passables — c'est exactement le trou qui rendait le
    # capstone RHCSA injouable sans que personne le sache.
    if runtime_type == "shell":
        _replay_shell_solution(lab_root, rel_path)
        return

    # Runtime VM : cherche solution.yaml côté formateur (solution/...)
    solution_yaml = REPO_ROOT / "solution" / rel_path / "solution.yaml"
    if not solution_yaml.is_file():
        # Solution absente : log puis skip soft (les tests tournent sur
        # l'état actuel — utile pour valider le travail manuel apprenant).
        return

    if host_name is None:
        raise RuntimeError(
            f"Lab {lab_root.name} : runtime.type=vm mais aucun "
            f"runtime.targets[].host trouvable. Vérifie lab.yaml."
        )

    # Joue solution.yaml via ansible-runner (cohérent avec dsoxlab run).
    # Import local pour éviter d'exiger dsoxlab installé pour les labs
    # shell-only.
    try:
        from dsoxlab.discovery.repo import read_repo_metadata
        from dsoxlab.infra import ansible as ansible_infra
        from dsoxlab.infra.inventory import build_inventory, read_terraform_outputs
    except ImportError:
        pytest.skip(
            f"[{lab_root.name}] dsoxlab non installé. Pour la validation "
            f"VM, lance 'uv tool install --editable ~/Projets/dsoxlab'."
        )

    repo_meta = read_repo_metadata(REPO_ROOT)
    if repo_meta is None:
        pytest.skip(f"[{lab_root.name}] meta.yml introuvable.")

    tf_outputs = read_terraform_outputs(repo_meta)
    inventory = build_inventory(
        repo_meta,
        terraform_outputs=tf_outputs,
        target_fqdn=host_name,
    )

    vault_password_file: Path | None = None
    vault_pass = REPO_ROOT / ".vault-pass"
    if vault_pass.is_file():
        vault_password_file = vault_pass

    result = ansible_infra.run_playbook(
        playbook_path=solution_yaml,
        inventory=inventory,
        vault_password_file=vault_password_file,
    )
    if not result.ok:
        raise RuntimeError(
            f"solution.yaml a échoué pour {lab_root.name} "
            f"(rc={result.rc}, status={result.status}). "
            f"Stats : {result.stats}"
        )
