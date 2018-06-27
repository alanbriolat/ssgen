def main(initial_args=None):
    import sys
    import os
    import argparse
    import logging

    from .site import Site

    parser = argparse.ArgumentParser()
    parser.add_argument('-g', '--generate', help='Generate output',
                        action='store_true', default=False)
    parser.add_argument('-f', '--force', help='Generate files even if up-to-date',
                        action='store_true', default=False)
    parser.add_argument('-d', '--debug', dest='loglevel',
                        action='store_const', const=logging.DEBUG, default=logging.INFO)
    parser.add_argument('-q', '--quiet', dest='loglevel',
                        action='store_const', const=logging.ERROR)
    parser.add_argument('--dir', help='Site directory [default: .]',
                        action='store', dest='directory', default=os.curdir)

    args = parser.parse_args(sys.argv[1:] if initial_args is None else initial_args)

    logging.basicConfig(level=args.loglevel)

    site = Site(args.directory)
    site.scan()
    if args.generate:
        site.generate(args.force)
