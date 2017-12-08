function KikiBeaubaExp1()
  % Kiki Bouba experiment code
  % Developed for Beau Sievers
  % Requires dlmcell.m and csvimport.m (simplifies csv writing/reading)
  %   - Will Haslett 1-May-13

  % One sound, two emotions.
  % Click on the corresponding emotion.

  % TODO: Only for development
  Screen('Preference','SkipSyncTests', 1);

  % Configuration varables
  %-----------------------------------------------------------------------------------------------------
  % Text file containing stimulus sets and pointer for next trial
  stimulusSetsFile = 'soundneg_stimulus_sets.csv';
  % Text file containing index for next stimulus set
  nextStimulusSetFile = 'soundneg_next_stimulus_set_index.txt'
  % Pixels between the two images, and from left/right screen edges to images
  imagePadding = 75;
  % Delay in milliseconds between the image presentation and the start of audio playback
  audioDelay = 500.0;
  % All images will be displayed at this aspect ratio (this is width/height)
  imageAspectRatio = 1.6;
  % Width in pixels of bounding highlight box. Use an even number.
  highlightWidth = 10;
  % Used for output file names. See http://www.mathworks.com/help/matlab/ref/datestr.html
  timeFormat = 'yy-mm-dd-HH-MM-SS';
  % File paths. Assume that './' (for this fie's directory) precedes your string
  % Supply a trailing file separator
  outputRelativePath = 'soundneg_output/';
  mediaPath = 'media/';

  % Declare variables that are needed by more than one nested function (for proper scope)
  %-----------------------------------------------------------------------------------------------------
  participantId = [];
  screenNumber = [];
  w = [];
  white = [];
  gray = [];
  black = [];
  screenWidth = [];
  screenHeight = [];
  screenCenterX = [];
  screenCenterY = [];
  numStimulusSets = [];
  stimulusIndex = [];
  leftImage = [];
  rightImage = [];
  leftImageCenterX = [];
  rightImageCenterX = [];
  leftImageOriginOffset = [];
  rightImageOriginOffset = [];
  displayedImageWidth = [];
  imageRectangle = [];
  highlightRectangle = [];
  leftImageRectangle = [];
  rightImageRectangle = [];
  thisDir = [];
  leftImageFileName = [];
  rightImageFileName = [];
  audioFileName = [];
  audioHandle = [];
  selectedImage = [];
  responseTimeSec = [];
  outputFileNameWithPath = [];
  timeToQuit = false;

  % Main program function calls
  %-----------------------------------------------------------------------------------------------------
  InitialSetup;
  InitializeWindow;
  while ~timeToQuit
    DefineMedia;
    IncrementStimulusIndex;
    LoadImages;
    LoadAudio;
    GetParticipantId;
    CreateOutputFile;
    WriteHeader;
    ShowIntroScreen;
    DrawImages;
    PlayAudio;
    GetImagePick;
    WriteOutputData;
    timeToQuit = true;
    OfferToContinue;
  end
  CleanUp;

  %-----------------------------------------------------------------------------------------------------
  function InitialSetup
    % Clear the console history and hide the cursor
    clc;
    AssertOpenGL;
    HideCursor;
    % Set path where this file lives
    thisDir = strrep(mfilename('fullpath'), mfilename, '');
    % Ensure consistent cross-platfrom keyboard mapping
    KbName('UnifyKeyNames');
    % Dummy calls to make sure that these functions don't cause delays later
    KbCheck;
    WaitSecs(0.1);
    GetSecs;
    % Set display index (prefers external if connected)
    screenNumber = max(Screen('Screens'));
    % Set colors
    white = WhiteIndex(screenNumber);
    gray = GrayIndex(screenNumber) / 1.5;
    black = BlackIndex(screenNumber);
    % Initialize sound driver
    InitializePsychSound;
  end
  %-----------------------------------------------------------------------------------------------------
  function InitializeWindow
    % Set maximum process priority
    Priority(MaxPriority(w));
    % Open fullscreen window, w is the handle for drawing commands
    % wRect is a rectangle that covers the entire screen

    %[w, wRect]=Screen('OpenWindow',screenNumber, gray);
    % Development only: Comment out the above and use the below for non-fullscreen
    [w, wRect]=Screen('OpenWindow',screenNumber, gray, [0 0 853 640]);

    % Set text size
    Screen('TextSize', w, 32);
    % Get screen size, set some coordinates, set some dimensions
    [screenWidth, screenHeight] = Screen('Windowsize', w);
    screenCenterX = floor(screenWidth / 2);
    screenCenterY = floor(screenHeight / 2);
    displayedImageWidth = floor((screenWidth - (3 * imagePadding)) / 2);
    imageRectangle = [(-1 * displayedImageWidth / 2) (-1 * displayedImageWidth / (2* imageAspectRatio)) (displayedImageWidth / 2) (displayedImageWidth / (2* imageAspectRatio))];
    highlightRectangle = imageRectangle + [(-1 * highlightWidth) (-1 * highlightWidth) highlightWidth highlightWidth];
    leftImageCenterX = floor(imagePadding + (displayedImageWidth / 2));
    leftImageOriginOffset = [leftImageCenterX screenCenterY leftImageCenterX screenCenterY];
    rightImageCenterX = floor((2 * imagePadding) + ((3 * displayedImageWidth) / 2));
    rightImageOriginOffset = [rightImageCenterX screenCenterY rightImageCenterX screenCenterY];
    leftImageRectangle = imageRectangle + leftImageOriginOffset;
    rightImageRectangle = imageRectangle + rightImageOriginOffset;
  end
  %-----------------------------------------------------------------------------------------------------
  function DefineMedia
    stimulusCsv = csvimport(char(strcat(thisDir, stimulusSetsFile)));
    % Count the rows to get the number of stimulus sets
    numStimulusSets = length(stimulusCsv(:,1));
    % The following line is absurd but it works and I'm in a hurry
    stimulusIndex = str2num(char(csvimport(char(strcat(thisDir, nextStimulusSetFile)))));
    leftImageFileName = stimulusCsv(stimulusIndex, 1);
    rightImageFileName = stimulusCsv(stimulusIndex, 2);
    audioFileName = stimulusCsv(stimulusIndex, 3);
  end
  %-----------------------------------------------------------------------------------------------------
  function IncrementStimulusIndex
    stimulusIndexFileId = fopen(strcat(thisDir, nextStimulusSetFile), 'w+');
    nextStimulusSetIndex = stimulusIndex + 1;
    % Reset to the first stimulus set when appropriate. Skip the header row.
    if stimulusIndex >= numStimulusSets
      nextStimulusSetIndex = 2;
    end
    disp(nextStimulusSetIndex);
    fprintf(stimulusIndexFileId, '%d', nextStimulusSetIndex);
    fclose(stimulusIndexFileId);
  end
  %-----------------------------------------------------------------------------------------------------
  function LoadImages
    leftImage = Screen('MakeTexture', w, imread(char(strcat(thisDir, mediaPath, leftImageFileName))));
    rightImage = Screen('MakeTexture', w, imread(char(strcat(thisDir, mediaPath, rightImageFileName))));
  end
  %-----------------------------------------------------------------------------------------------------
  function LoadAudio
    [wavDataInverse, wavDataSampleFrequency] = wavread(char(strcat(thisDir, mediaPath, audioFileName)));
    wavData = wavDataInverse';
    numChannels = size(wavData, 1);
    if numChannels < 2
      wavData = [wavData; wavData];
      numChannels = 2;
    end
    audioHandle = PsychPortAudio('Open', [], [], 0, wavDataSampleFrequency, numChannels);
    PsychPortAudio('FillBuffer', audioHandle, wavData);
  end
  %-----------------------------------------------------------------------------------------------------
  function GetParticipantId
    ListenChar(2);
    participantId = GetEchoString(w, 'Participant ID:', 20, screenCenterY, white, black);
    Screen('Flip', w);
    ListenChar(0);
  end
  %-----------------------------------------------------------------------------------------------------
  function CreateOutputFile
    outputFileNameWithPath = strcat(thisDir, outputRelativePath, 'participant_', participantId, '_', datestr(clock, timeFormat), '.csv');
    outputFile= fopen(outputFileNameWithPath, 'w+');
    fclose(outputFile);
  end
  %-----------------------------------------------------------------------------------------------------
  function WriteHeader
    header = {'participantId' 'stimulusSet' 'leftImage' 'rightImage' 'audioFile' 'selectedImage' 'responseTime'};
    dlmcell(outputFileNameWithPath, header, ',');
  end
  %-----------------------------------------------------------------------------------------------------
  function ShowIntroScreen
    message = 'The next screen is for the participant...';
    DrawFormattedText(w, message, 'center', 'center', white);
    Screen('Flip', w);
    pause(2);
    message = 'When you are ready, press any key to begin';
    DrawFormattedText(w, message, 'center', 'center', white);
    Screen('Flip', w);
    ListenChar(2);
    KbWait;
    ListenChar(0);
  end
  %-----------------------------------------------------------------------------------------------------
  function DrawImages
    Screen('DrawTexture', w, leftImage, [], leftImageRectangle);
    Screen('DrawTexture', w, rightImage, [], rightImageRectangle);
    Screen('Flip', w);
    % Start the response timer here
    tic;
  end
  %-----------------------------------------------------------------------------------------------------
  function PlayAudio
    WaitSecs(audioDelay / 1000.0);
    startTime = PsychPortAudio('Start', audioHandle, 1, 0, 1);
  end
  %-----------------------------------------------------------------------------------------------------
  function HighlightImage(leftOrRight, onOrOff)
    switch leftOrRight
      case 'left'
        originOffset = leftImageOriginOffset;
      case 'right'
        originOffset = rightImageOriginOffset;
    end
    switch onOrOff
      case 'on'
        frameColor = (gray + white) / 2;
      case 'off'
        frameColor = gray;
    end
    Screen('FrameRect', w , frameColor, highlightRectangle + originOffset, highlightWidth);
    DrawImages;
  end
  %-----------------------------------------------------------------------------------------------------
  function GetImagePick
    SetMouse(floor(screenWidth / 2), floor(0.9 * screenHeight), w);
    ShowCursor;
    leftHighlighted = false;
    rightHighlighted = false;
    while true
      [x, y, buttons] = GetMouse(w);
      imageFocus = currentImageFocus(x, y);
      % When the mouse is not over either image
      if  (strcmp(imageFocus, 'none'))
        if leftHighlighted == true
          leftHighlighted = false;
          HighlightImage('left', 'off');
        end
        if rightHighlighted == true
          rightHighlighted = false;
          HighlightImage('right', 'off');
        end
        continue;
      end
      % When the mouse is over the left image
      if  (strcmp(imageFocus, 'left'))
        if leftHighlighted == false
          leftHighlighted = true;
          HighlightImage('left', 'on');
        end
        if rightHighlighted == true
          rightHighlighted = false;
          HighlightImage('right', 'off');
        end
      end
      % When the mouse is over the right image
      if  (strcmp(imageFocus, 'right'))
        if leftHighlighted == true
          leftHighlighted = false;
          HighlightImage('left', 'off');
        end
        if rightHighlighted == false
          rightHighlighted = true;
          HighlightImage('right', 'on');
        end
      end
      % Set selected image and exit loop if the left mouse button has been pressed
      if buttons(1)
        responseTimeSec = toc;
        selectedImage = imageFocus;
        HideCursor;
        break;
      end
    end
  end
  %-----------------------------------------------------------------------------------------------------
  function returnFocus = currentImageFocus(x, y)
    returnFocus = 'none';
    % Both images have the same y range, so test that first
    if y >= leftImageRectangle(2) & y <= leftImageRectangle(4)
      % Is the mouse in the x range of the left image?
      if x >= leftImageRectangle(1) & x <= leftImageRectangle(3)
        returnFocus = 'left';
      end
      % is the mouse in the x range of the right image?
      if x >= rightImageRectangle(1) & x <= rightImageRectangle(3)
        returnFocus = 'right';
      end
    end
  end
  %-----------------------------------------------------------------------------------------------------
  function WriteOutputData
    outData = {participantId stimulusIndex leftImageFileName rightImageFileName audioFileName selectedImage responseTimeSec};
    dlmcell(outputFileNameWithPath, outData, ',', '-a');
  end
  %-----------------------------------------------------------------------------------------------------
  function OfferToContinue
    message = 'Thank you.\nPlease let the reseach assistant take over the computer.';
    DrawFormattedText(w, message, 'center', 'center', white);
    Screen('Flip', w);
    pause(3);
    Screen('Flip', w);
    message = 'Run another trial? y/n';
    DrawFormattedText(w, message, 'center', 'center', white);
    Screen('Flip', w);
    ListenChar(2);
    FlushEvents;
    ynChosen = false;
    while ~ynChosen
      [character, when]  = GetChar;
      if character == 'n'
        timeToQuit = true;
        ynChosen = true;
      end
      if character == 'y'
        timeToQuit = false;
        ynChosen = true;
      end
    end
    ListenChar(0);
  end
  %-----------------------------------------------------------------------------------------------------
  function CleanUp
    ShowCursor;
    Screen('CloseAll');
    PsychPortAudio('Close', audioHandle);
    Priority(0);
  end
end
