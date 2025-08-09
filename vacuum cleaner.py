import time

print("Choose a Vacuum Cleaner Mode:")
print("1. Heavy-Duty (Stones and Dust)")
print("2. Medium (Some Dust)")
print("3. Surface Clean (Just Cleaning)")
print("4. Dust Vacuum (Fully Dusty Areas)")

mode = input("Enter vacuum mode (1-4): ")

if mode not in ['1', '2', '3', '4']:
    print("Invalid mode. Exiting program.")
else:
    mode = int(mode)
    state = 'OFF'

    if mode == 1:
        load = "Stones + Heavy Dust"
    elif mode == 2:
        load = "Moderate Dust"
    elif mode == 3:
        load = "Surface Cleaning Only"
    elif mode == 4:
        load = "Full Dust Cleaning"

    while True:
        print("\nCommands: start, stop, right, left, exit")
        cmd = input("Enter command: ").lower()

        if cmd == 'start':
            state = 'ON'
            print(f"\nMode {mode} started. Load type: {load}")
            if mode == 1:
                print("Heavy-Duty Vacuum: Suction system activated for stones and thick dust.")
            elif mode == 2:
                print("Medium Vacuum: Ready to clean light dust.")
            elif mode == 3:
                print("Surface Cleaner: Light polish mode enabled.")
            elif mode == 4:
                print("Dust Vacuum: High suction for dusty environments.")
            
            print("\nTimer started for 5 minutes... (simulated for 10 seconds)")
            
            # Use 300 for real 5 minutes
            for i in range(10, 0, -1):  # replace 10 with 300 for real timer
                print(f"Time remaining: {i} seconds", end='\r')
                time.sleep(1)

            print(f"\n5 minutes completed for Mode {mode}.\n")

            # After timer ends, state goes OFF
            state = 'OFF'
            print("Vacuum automatically stopped after timer.")
            print("You can enter a new command (start, stop, etc.)")

        elif cmd == 'stop':
            state = 'OFF'
            print(f"Mode {mode} stopped manually.")

        elif cmd == 'right':
            if state != 'ON':
                print("Please start the vacuum first.")
            else:
                if mode == 1:
                    print("Heavy-Duty Vacuum slowly turns right.")
                elif mode == 2:
                    print("Medium Vacuum turns right.")
                elif mode == 3:
                    print("Surface Cleaner shifts slightly right.")
                elif mode == 4:
                    print("Dust Vacuum redirects suction to the right.")

        elif cmd == 'left':
            if state != 'ON':
                print("Please start the vacuum first.")
            else:
                if mode == 1:
                    print("Heavy-Duty Vacuum slowly turns left.")
                elif mode == 2:
                    print("Medium Vacuum turns left.")
                elif mode == 3:
                    print("Surface Cleaner shifts slightly left.")
                elif mode == 4:
                    print("Dust Vacuum redirects suction to the left.")

        elif cmd == 'exit':
            print("Exiting program. Goodbye!")
            break

        else:
            print("Unknown command. Try again.")
