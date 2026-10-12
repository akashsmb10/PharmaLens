import argparse
from src.ingest import ingest
from src.validate import validate
from src.inspect_data import inspect_data
from src.documentation import dictionary

def main():
    parser = argparse.ArgumentParser(description="Phase 1 acquisition, validation and data understanding")
    parser.add_argument('--synthetic', action='store_true', help='Explicit offline demo only')
    parser.add_argument('--phase', type=int, choices=[1,2,3,4,5], default=1, help='Phase 1 acquisition, Phase 2 SQL, Phase 3 statistics, Phase 4 forecasting, or Phase 5 decisions')
    args = parser.parse_args()
    if args.phase == 5:
        if args.synthetic: parser.error('Phase 5 requires verified observed inputs and frozen forecasts')
        from src.phase5_pipeline import run_phase5
        run_phase5()
        return
    if args.phase == 4:
        if args.synthetic:
            parser.error('Phase 4 requires verified observed data')
        from src.phase4_pipeline import run_phase4
        run_phase4()
        return
    if args.phase == 3:
        if args.synthetic:
            parser.error('Phase 3 requires verified observed Phase 2 outputs')
        from src.phase3_pipeline import run_phase3
        run_phase3()
        return
    if args.phase == 2:
        if args.synthetic:
            parser.error('Phase 2 uses protected observed data; --synthetic is Phase 1 only')
        from src.phase2_pipeline import run_phase2
        run_phase2()
        return
    _, _, manifest = ingest(synthetic=args.synthetic)
    result = validate()
    inspect_data()
    dictionary()
    print(f"Mode={manifest['mode']} Raw={result['raw_rows']} Monthly={result['monthly_rows']} Audit passed={result['passed']}")
    raise SystemExit(0 if result['passed'] else 1)

if __name__ == '__main__':
    main()
