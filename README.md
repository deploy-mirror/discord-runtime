# Discord Bot – Ansible Deployment Repository

This repository contains the source code for a **personal Discord bot** that is **deployed and managed exclusively via Ansible**.
A lot of this code was vibe coded and is not clean.


It is **not** intended to be:
- a reusable library
- a plug-and-play Discord bot
- a documented or supported project

The code is public **only** so it can be pulled by Ansible during automated deployments.

This repository is **not accepting issues or pull requests**.

---

## Deployment model

- The bot is deployed using **Ansible**
- Configuration is provided **at runtime** via environment variables
- Secrets are **not stored** in this repository
- The service is run via **systemd**

If you are not deploying this with Ansible, this repository is likely not useful to you.

---

## Configuration

All configuration is provided via environment variables at runtime.

A `.env.example` file may be present for reference.
Actual secrets are never committed.
