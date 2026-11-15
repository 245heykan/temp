
    print(f"\n✅ Canali TV OK:    {len(tv_ok)}/{len(results_tv)}" +
          (" (ABORT)" if aborted else ""))
    print(f"✅ Eventi unici OK: {len(results_ev)}/{len(results_ev_raw)}")
    print(f"📄 {CHANNELS_OUTPUT} | {EVENTS_OUTPUT}")


if __name__ == "__main__":
    main()
