import argparse
import os
import shlex
from exceptions import FoogleException
from foogle import Foogle
from query import Query


class MyParser(argparse.ArgumentParser):
    def exit(self, status=0, message=None):
        pass

    def error(self, message=None):
        pass

    def print_help(self, file=None):
        pass


if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser("Foogle")
        parser.add_argument("path", type=str, help="Path to the directory "
                                                   "to work with.")
        args = parser.parse_args()
        try:
            if not os.path.isdir(args.path) or not os.path.exists(args.path):
                exit(">> Invalid folder.")
            print("\n>> Indexation has been started. Please wait..")
            foogle = Foogle(directory=args.path)
            print(">> Indexation has been ended.\n\nYou can use commands now.\n"
                  "Supported commands: indexof, relevant, help. "
                  "More info in README.md.\n")
        except OSError as e:
            print(e)
            exit(1)
        except Exception as e:
            print("Something went wrong.")
            exit(2)

        command_parser = MyParser(add_help=False)
        subparsers = command_parser.add_subparsers(dest="command")

        indexof_parser = subparsers.add_parser("indexof")

        relevant_parser = subparsers.add_parser("relevant")

        help_parser = subparsers.add_parser("help")

        for subparser in [indexof_parser, relevant_parser]:
            subparser.add_argument("-l", "--logic", action='store_true')
            subparser.add_argument("query", type=str)
            subparser.add_argument("-ext", "--extensions", type=str,
                                   default="!")

        relevant_parser.add_argument("-n", "--top-n", type=int, default=3)

        while True:
            try:
                print(">", end=" ")
                args = command_parser.parse_args(shlex.split(input()))
                if args.command == "help":
                    print("https://www.youtube.com/watch?v=yD2FSwTy2lw")
                    continue
                query = Query(args.query, args.logic).data
                extensions = {f".{ext}" for ext in args.extensions.split()} \
                    .intersection(Foogle.SUPPORTED_EXTENSIONS)
                if len(extensions) == 0:
                    extensions = Foogle.SUPPORTED_EXTENSIONS
                match args.command:
                    case "indexof":
                        found = (foogle.search(query, extensions))
                        if len(found) == 0:
                            print("Nothing has been found.")
                        else:
                            print(f"--- {len(found)} document(s) "
                                  f"have been found:")
                            for i, path in enumerate(found):
                                print(f"{i + 1}. {path}")
                    case "relevant":
                        n = args.top_n
                        if n < 1:
                            n = 3
                        most_relevant_documents = foogle.relevant(
                            query, extensions, n
                        )
                        if len(most_relevant_documents) == 0:
                            print("Nothing has been found.")
                        else:
                            count = min(n, len(most_relevant_documents))
                            print(f"--- Top {count} most relevant documents:")
                            for i, document in enumerate(
                                    most_relevant_documents):
                                print(f"{i + 1}. {document}")
            except OSError as e:
                print(e)
            except FoogleException as e:
                print(e)
            except Exception as e:
                print("Something went wrong. Try again.")
            finally:
                print()
    except KeyboardInterrupt:
        pass
