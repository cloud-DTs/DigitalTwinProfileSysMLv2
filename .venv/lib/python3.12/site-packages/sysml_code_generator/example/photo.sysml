package PhotoExample {
    action focus;
    action shoot;

    action takePicture {
        first focus;
        then shoot;
        then done;
    }
}
