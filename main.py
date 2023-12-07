import argparse
import os.path

from exceptions import *
from foogle import Foogle
from query import Query

if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser("Foogle")
        parser.add_argument("path", type=str, help="Path to the directory "
                                                   "to work with.")
        args = parser.parse_args()
        try:
            if not os.path.isdir(args.path) or not os.path.exists(args.path):
                exit("Invalid folder.")
            print("Indexation has been started. Please wait..")
            foogle = Foogle(directory=args.path)
            foogle.index()
            print("Indexation has been ended. You can use commands now.")
        except OSError as e:
            print(e)
        except Exception as e:
            print("Something went wrong.")
            exit(1)

        command_parser = argparse.ArgumentParser(exit_on_error=False,
                                                 add_help=False)
        command_parser.add_argument("command", type=str)
        command_parser.add_argument("query", type=str)

        subparsers = command_parser.add_subparsers(dest="command")
        indexof_parser = subparsers.add_parser("indexof",
                                               exit_on_error=False)

        relevant_parser = subparsers.add_parser("relevant",
                                                exit_on_error=False)

        supported_commands = ["indexof", "relevant"]
        _help = "No one's around to help."
        while True:
            try:
                inpstr = input()
                if inpstr == "--help" or inpstr == "-h":
                    print(_help)
                    continue
                inpsplit = inpstr.split()
                command, query = inpsplit[0], " ".join(inpsplit[1:])
                if command not in supported_commands:
                    print("Wrong command. Use --help to find some help.")
                    continue
                args = command_parser.parse_args([command, query])
                query = args.query
                print("----------")
                match command:
                    case "indexof":
                        query = Query(query).data
                        found = (foogle.search(query))
                        if len(found) == 0:
                            print("Nothing has been found.")
                        else:
                            print(f"{len(found)} document(s) have been found:")
                            for path in found:
                                print(path)
                    case "relevant":
                        split_query = query.split()
                        if split_query[0] == "-n":
                            n = int(split_query[1])
                            query = "".join(split_query[2:])
                        else:
                            n = 3
                        if n < 1:
                            n = 1
                        query = Query(query).data
                        most_relevant_documents = foogle.relevant(query, n)
                        if len(most_relevant_documents) == 0:
                            print("Nothing has been found.")
                        else:
                            print(f"Top {n} most relevant documents:")
                            for i, document in enumerate(
                                    most_relevant_documents):
                                print(f"{i + 1}) {document}")
                print()
            except OSError as e:
                print(e)
            except FoogleException as e:
                print(e)
            except Exception as e:
                print("Something went wrong. Try again.")
    except KeyboardInterrupt:
        pass
