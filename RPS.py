# The example function below keeps track of the opponent's history and plays whatever the opponent played two plays ago. It is not a very good player so you will need to change the code to pass the challenge.

def player(prev_play, opponent_history=[]):
    opponent_history.append(prev_play)

    guess = "R"
    if len(opponent_history) > 2:
        guess = opponent_history[-2]

    return guess

    def counter(move):
        return beats[move]

    # --- Persistent state (kept across calls via default args) ---
    if not hasattr(player, "my_history"):
        player.my_history = []
    if not hasattr(player, "pair_counts"):
        # for modeling Abbey: counts of what we played AFTER a 2-move sequence
        player.pair_counts = {}

    # Reset between matches (FCC sends prev_play == "" at first round of a match)
    if prev_play == "":
        opponent_history.clear()
        player.my_history = []
        player.pair_counts = {}
        # start with something safe
        return "R"

    # record opponent move
    opponent_history.append(prev_play)

    # --- Update Abbey-model counts using our own history ---
    # If we have at least 3 of our own plays, then we can update the mapping:
    # (my[-3], my[-2]) -> my[-1]
    if len(player.my_history) >= 3:
        pair = player.my_history[-3] + player.my_history[-2]
        nxt = player.my_history[-1]
        if pair not in player.pair_counts:
            player.pair_counts[pair] = {"R": 0, "P": 0, "S": 0}
        player.pair_counts[pair][nxt] += 1

    # --- Bot detection ---
    # 1) Quincy cycles: R, P, S, R, P repeating (common FCC bot)
    quincy_cycle = ["R", "P", "S", "R", "P"]
    is_quincy = False
    if len(opponent_history) >= 5:
        is_quincy = all(opponent_history[i] == quincy_cycle[i % 5] for i in range(len(opponent_history)))

    # 2) Kris: plays the move that BEATS our previous move
    # If opponent often equals counter(our_last), it's Kris.
    is_kris = False
    if len(player.my_history) >= 2 and len(opponent_history) >= 2:
        checks = 0
        hits = 0
        # check last up to 20 comparisons
        for i in range(1, min(21, len(opponent_history), len(player.my_history) + 1)):
            # opponent at -i should equal counter(our at -(i+1))
            opp = opponent_history[-i]
            my_prev = player.my_history[-(i + 1)]
            checks += 1
            if opp == counter(my_prev):
                hits += 1
        if checks >= 6 and hits / checks >= 0.8:
            is_kris = True

    # 3) Mrugesh: often counters our most common move in last ~10 plays
    is_mrugesh = False
    if len(player.my_history) >= 12 and len(opponent_history) >= 12:
        window = player.my_history[-11:-1]  # last 10 moves BEFORE our last move
        freq = {"R": 0, "P": 0, "S": 0}
        for m in window:
            freq[m] += 1
        most_common = max(freq, key=freq.get)
        predicted_opp = counter(most_common)  # what Mrugesh would play
        # If opponent recently matches that prediction a lot -> Mrugesh
        checks = 0
        hits = 0
        for i in range(1, 11):
            # recompute each step roughly using sliding window behind that point
            if len(player.my_history) < i + 11:
                break
            w = player.my_history[-(i + 11):-(i + 1)]
            f = {"R": 0, "P": 0, "S": 0}
            for m in w:
                f[m] += 1
            mc = max(f, key=f.get)
            pred = counter(mc)
            checks += 1
            if opponent_history[-i] == pred:
                hits += 1
        if checks >= 6 and hits / checks >= 0.7:
            is_mrugesh = True

    # If not Quincy / Kris / Mrugesh, assume Abbey (the “predict your next move” bot)
    is_abbey = (not is_quincy) and (not is_kris) and (not is_mrugesh)

    # --- Choose move based on detected opponent ---
    my_move = "R"

    if is_quincy:
        # predict next in the known cycle, then counter it
        next_opp = quincy_cycle[len(opponent_history) % 5]
        my_move = counter(next_opp)

    elif is_kris:
        # Kris plays counter(our_last). To beat Kris:
        # if our last was X, Kris plays counter(X), so we play counter(counter(X))
        last = player.my_history[-1] if player.my_history else "R"
        my_move = counter(counter(last))

    elif is_mrugesh:
        # Mrugesh tends to play counter(most_common(last10_of_us)).
        # Predict his move from our last 10, then counter it.
        window = player.my_history[-10:] if len(player.my_history) >= 10 else player.my_history[:]
        freq = {"R": 0, "P": 0, "S": 0}
        for m in window:
            freq[m] += 1
        most_common = max(freq, key=freq.get) if window else "R"
        predicted_opp = counter(most_common)
        my_move = counter(predicted_opp)

    else:
        # Abbey model: she predicts our next move based on our last two moves,
        # then plays the counter to that predicted move.
        if len(player.my_history) >= 2:
            pair = player.my_history[-2] + player.my_history[-1]
            if pair in player.pair_counts:
                counts = player.pair_counts[pair]
                predicted_my_next = max(counts, key=counts.get)
            else:
                predicted_my_next = "R"
        else:
            predicted_my_next = "R"

        abbey_play = counter(predicted_my_next)
        my_move = counter(abbey_play)

    # record our move for next call
    player.my_history.append(my_move)
    return my_move
