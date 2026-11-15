#!/usr/bin/env bash
# Wrapper: /mnt/h is world-writable in WSL, so ansible would ignore ./ansible.cfg.
# Point ANSIBLE_CONFIG at it explicitly and use the venv with ansible-core.
cd "$(dirname "$0")"
export ANSIBLE_CONFIG="$PWD/ansible.cfg" ANSIBLE_FORCE_COLOR=0 PATH="$HOME/ansible-venv/bin:$PATH"
exec "$@"
