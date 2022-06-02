*** Settings ***
Library     video_recorder.py
Library     RPA.Browser.Selenium


*** Tasks ***
Video Recording Example
    [Setup]    Start Recorder    filename=output/recording.mp4    fps=20    scale=0.5    force_fps=True    #compress=False
    Open Available Browser    https://robocorp.com/docs
    Sleep    2s
    Input Text    //input[@placeholder='Search']    SpaceX
    Sleep    2s
    Click Link    (//a[h3])[1]
    Sleep    3s
    Close All Browsers
    # [Teardown]    Store Video Only If Run Fails
    [Teardown]    Stop Recorder


*** Keywords ***
Store Video Only If Run Fails
    Run Keyword If Test Failed    Stop Recorder
    Run Keyword If Test Passed    Cancel Recorder
