# Migrating from qtplasmac

If you already have a working qtplasmac configuration, you can convert it to MonoKrom:

```bash
# Interactive wizard
monokrom_plasma setup --wizard --from-config ~/linuxcnc/configs/my_qtplasmac_config

# Non-interactive
monokrom_plasma setup --from-config ~/linuxcnc/configs/my_qtplasmac_config
```

See [Config Migration](../integrator-guide/config-migration.md) for full details.
