import argparse
import json
import sys

from sqlmodel import Session

from app.database import create_db_and_tables, engine
from app.errors import DomainError
from app.incident_service import build_summary
from app.seed import reset_demo_data


def main() -> None:
    parser = argparse.ArgumentParser(description="Incident tracking admin tool")
    commands = parser.add_subparsers(dest="command", required=True)
    summary = commands.add_parser("bilan", help="Count incidents by state and severity")
    summary.add_argument("--format", choices=["json"], default="json")
    commands.add_parser("reset-demo", help="Wipe the demo database and reload fictional data")
    args = parser.parse_args()

    create_db_and_tables()
    with Session(engine) as session:
        if args.command == "bilan":
            print(json.dumps(build_summary(session), indent=2))
        elif args.command == "reset-demo":
            try:
                reset_demo_data(session)
            except DomainError as error:
                print(f"Error: {error.detail}", file=sys.stderr)
                sys.exit(1)
            print("Demo data reset: alice and bob (declarant), carol (analyste)")


if __name__ == "__main__":
    main()
