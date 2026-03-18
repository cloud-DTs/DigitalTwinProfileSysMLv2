package TrafficLightExample {
    action play_sound;

    state TrafficLight {
        attribute has_malfunction : ScalarValues::Boolean;

        state RED;
        state GREEN;
        state YELLOW;
        state YELLOW_BLINKING;

        entry; then YELLOW_BLINKING;

        transition yellow_blinking_to_red
            first YELLOW_BLINKING
            if not has_malfunction
            then RED;

        transition red_to_green
            first RED
            do play_sound
            then GREEN;

        transition green_to_yellow
            first GREEN
            then YELLOW;

        transition yellow_to_red
            first YELLOW
            then RED;

        transition red_to_blinking
            first RED
            if has_malfunction
            then YELLOW_BLINKING;

        transition yellow_to_blinking
            first YELLOW
            if has_malfunction
            then YELLOW_BLINKING;

        transition green_to_blinking
            first GREEN
            if has_malfunction
            then YELLOW_BLINKING;
    }
}
