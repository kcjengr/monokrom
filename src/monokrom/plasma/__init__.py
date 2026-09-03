import os
import sys
from . import monokrom_rc as monokrom_rc
import monokrom

VCP_DIR = os.path.realpath(os.path.dirname(__file__))
VCP_CONFIG_FILE = os.path.join(VCP_DIR, 'config.yml')


def _parse_setup_args(argv=None):
    """Parse setup subcommand arguments.

    Returns a dict with keys: wizard, from_config, auto, output_dir.
    """
    args = argv if argv is not None else sys.argv[1:]
    result = {
        'wizard': False,
        'auto': False,
        'from_config': None,
        'output_dir': None,
    }

    i = 0
    while i < len(args):
        arg = args[i]
        if arg == '--wizard':
            result['wizard'] = True
        elif arg == '--auto':
            result['auto'] = True
        elif arg == '--from-config' and i + 1 < len(args):
            result['from_config'] = args[i + 1]
            i += 1
        elif arg == '--output-dir' and i + 1 < len(args):
            result['output_dir'] = args[i + 1]
            i += 1
        elif arg.startswith('--from-config='):
            result['from_config'] = arg.split('=', 1)[1]
        elif arg.startswith('--output-dir='):
            result['output_dir'] = arg.split('=', 1)[1]
        i += 1

    return result


def main(opts=None):
    # Check for 'setup' subcommand in sys.argv
    if opts is None:
        args = sys.argv[1:]
        if 'setup' in args:
            setup_args = _parse_setup_args(args)
            if not setup_args['from_config']:
                print("Error: --from-config <path> is required for setup command", file=sys.stderr)
                sys.exit(1)

            from . import setup

            if setup_args['wizard']:
                # Interactive wizard mode
                wizard = setup.Wizard(
                    source_dir=setup_args['from_config'],
                    output_dir=setup_args['output_dir'],
                )
                wizard.run()
            else:
                # Non-interactive mode
                setup.run(
                    source_dir=setup_args['from_config'],
                    output_dir=setup_args['output_dir'],
                    auto=setup_args['auto'],
                )
            return

    monokrom.main('plasma', opts)


if __name__ == '__main__':
    main()
