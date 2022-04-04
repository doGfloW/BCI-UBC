clear all
close all
myDir = uigetdir

% get all text data files from the directory
myFiles = dir(fullfile(myDir,'*.txt'));

% loop through each data file
for k = 1:length(myFiles)
    % load current file
    baseFileName = myFiles(k).name;
    fullFileName = fullfile(myDir, baseFileName);
    try
        data = dlmread(fullFileName, '\t');
    catch
        data = dlmread(fullFileName, ',');
    end
    fprintf(1, 'Now reading %s\n', fullFileName);

    r_channel = [];
    markers = data(:,end);
    [~, data_col] = size(data);
    
    % check if the data file contains cyton or ganglion data (cyton has 24 columns in a text file)
    if data_col == 24
        last_channel = 9; % cyton
    else
        last_channel = data_col-2; % ganglion
    end
    
    % loop through each channel in the data file
    for channel=2:last_channel
        EEG = data(:,channel)*1E-6;
        
        % if channel==3 ||channel==4 || channel==5 || channel==7  || channel==8 && last_channel==9
        %     EEG=EEG-(data(:,last_channel)*1E-6);
        % end
        
        % apply bandpass to the alpha and beta frequency bands
        apass = bandpass(EEG,[8 13], 250);
        bpass = bandpass(EEG,[13 32], 250);

        % find peaks in the last column of the data (marker column)
        [pks,locs] = findpeaks(data(:, end));
        marker = [locs,pks];
        
        % get FFT of the alpha frequency band values
        a_fft = fft(apass);
        
        l = length(pks);
        c = 1;

        T1 = zeros(200,1);
        T2 = zeros(200,1);
        
        % loop through each section which is divided by the markers (peaks)
        for count = 1:length(pks)
            if pks(count) <= 2
                T1(c) = locs(count);
                event(c,1) = 1;
                if pks(count) == 2
                    event(c,1) = 0;
                end
                c = c + 1;
            end
        end
        
        c = 1;
        for count = 1:length(pks)
            if pks(count) > 10
                T2(c) = locs(count);
                c = c + 1;
            end
        end
        
        % initialize five arrays to save memory
        T1 = nonzeros(T1);
        T2 = nonzeros(T2);
        abandpower = zeros(20,1);
        bbandpower = zeros(20,1);
        r = zeros(1,20);
        M = [T1,T2]; 
        
        % loop through the M array
        for k = 1:length(M)
            if M(k) == 0
                break
            end
            
            i = M(k,1);
            j = M(k,2);
            
            % apply bandpass filter to get the akpha and beta values
            abandpower(k) = bandpower(apass(i:j));
            bbandpower(k) = bandpower(bpass(i:j));
            r(k) = abandpower(k) / bbandpower(k);
        end
        
        % append values to final array
        temp = r_channel;
        r_channel = [temp,r];   

        % initialize arrays again
        abandpower = nonzeros(abandpower);
        bbandpower = nonzeros(bbandpower);
        r = nonzeros(r);
    end
    
    % write this file's output to a new file
    bp = [r_channel, event];
    dataset_folder = cd;
    dataset_folder = fullfile(dataset_folder, "BCI-UBC", "Datasets");
    wfilename = "new_8.xlsx";
    dataset_folder = fullfile(dataset_folder, wfilename);

    if isfile(dataset_folder)
        fprintf("Dataset Found now adding to data set %s\n", dataset_folder)
    else
        %cols_name = {}
        xlswrite(dataset_folder, {1, 2, 3, 4, 5, 6, 7, 8, 9})
        fprintf('Created new dataset called %s\n', dataset_folder)
    end
    
    read_data = table2array(readtable(dataset_folder));
    write_data = [read_data; bp];
    writematrix(write_data, dataset_folder); 
end

fprintf('done')
