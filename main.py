import content_handler
import argparse


if __name__ == "__main__":

    a = argparse.ArgumentParser()
    a.add_argument("url", help="save parser file from url")
    a.add_argument("--f", help="file with configs")
    args = a.parse_args()

    handler = content_handler.ContentHandler()
    print(handler.write_content_to_file(args.url, args.f))

