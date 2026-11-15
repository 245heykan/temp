
            buffer_tags.append(line)
        elif line.startswith("#EXTVLCOPT"):
            buffer_vlcopt.append(line)
        elif line.strip():
            url = line.strip()
            # Convert VLC options to HTTP headers
            headers = {}
            for opt in buffer_vlcopt:
                if opt.startswith("#EXTVLCOPT:"):
                    key_value = opt[len("#EXTVLCOPT:"):].split("=", 1)
                    if len(key_value) == 2:
                        key, value = key_value
                        key = key.lower()
                        if key == "http-referrer":
                            headers["Referer"] = value
                        elif key == "http-origin":
                            headers["Origin"] = value
                        elif key == "http-user-agent":
                            headers["User-Agent"] = value

            print(f"Checking: {url}")
            if is_stream_playable(url, headers=headers):
                print("  ✓ Playable")
                output_lines.extend(buffer_tags)
                output_lines.extend(buffer_vlcopt)
                output_lines.append(url)
            else:
                print("  ✗ Not playable")

            buffer_tags = []
            buffer_vlcopt = []

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines) + "\n")

    print(f"\nSaved filtered playlist to: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python filter liveeventsfilter.py input.m3u output.m3u")
        sys.exit(1)

    input_m3u = sys.argv[1]
    output_m3u = sys.argv[2]

    if not Path(input_m3u).exists():
        print("Input file does not exist.")
        sys.exit(1)

    filter_m3u_playlist(input_m3u, output_m3u)
