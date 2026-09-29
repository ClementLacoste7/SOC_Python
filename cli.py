import argparse
import json

from sqlmodel import Session

from app.database import create_db_and_tables, engine
from app.incident_service import build_summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Incident tracking admin tool")
    commands = parser.add_subparsers(dest="command", required=True)
    summary = commands.add_parser("bilan", help="Count incidents by state and severity")
    summary.add_argument("--format", choices=["json"], default="json")
    args = parser.parse_args()

    create_db_and_tables()
    with Session(engine) as session:
        if args.command == "bilan":
            print(json.dumps(build_summary(session), indent=2))


if __name__ == "__main__":
    main()
