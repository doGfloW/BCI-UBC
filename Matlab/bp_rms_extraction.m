function [bp_class, rms_class, bp_values, rms_values] = bp_rms_extraction(input_data, live_yn)
    % check if the data is character/string or 2D numerical array
    % if ischar(input_data) | isstring(input_data)
    %     % read data from text file
    %     try
    %         data = dlmread(convertCharsToStrings(input_data), '\t');
    %     catch
    %         data = dlmread(convertCharsToStrings(input_data), ',');
    %     end
    % else
    %     % assign the data to a variable
    %     data = input_data
    % end

    try
        data = dlmread(convertCharsToStrings(input_data), '\t');
    catch
        data = dlmread(convertCharsToStrings(input_data), ',');
    end

    % define the data size and the output array
    [data_row, data_col] = size(data);
    alldata = [];
    bp_values = [];
    rms_values = [];

    if data_col == 24
        last_channel = 9; % cyton
        f = 250;
    else
        last_channel = data_col-2; % ganglion
        f = 200;
    end

    if live_yn == 1
        % loop through each channel in the data
        for channel = 2:(last_channel)
            % store data for the current channel
            eeg_channel_data = data(:,channel);
            % if channel==3 ||channel==4 || channel==5 || channel==7  || channel==8 && last_channel==9
                % eeg_channel_data=eeg_channel_data-(data(:,last_channel));
            % end


            % pass channel data through a bandpass filter
            alpha_bandpass = bandpass(eeg_channel_data, [8 13], f);
            beta_bandpass = bandpass(eeg_channel_data, [13 32], f);

            for x= 1:350
                 alpha_bandpass(1,:) = [];
                 alpha_bandpass(end,:) = [];
                 beta_bandpass(1,:) = [];
                 beta_bandpass(end,:) = [];
                x=x+1;
            end
            % get bandpower and rms values
            alpha_bp = bandpower(alpha_bandpass);
            beta_bp = bandpower(beta_bandpass);
            alpha_rms = rms(alpha_bandpass);
            beta_rms = rms(beta_bandpass);


            % find peaks of the filtered data
            % [peaks, locs]=findpeaks(data(:, 15));

            % append values to the outputs
            bp_values(end+1) = alpha_bp/beta_bp;
            rms_values(end+1) = alpha_rms/beta_rms;
        end

        if  last_channel == 9
            [bp_class] = BP_classification_cyton(bp_values);
            [rms_class] = RMS_classification_cyton(rms_values);
        else
            [bp_class] = BP_classification(bp_values);
            [rms_class] = RMS_classification(rms_values);
        end

    else
        segment = 0;
        counter = 0;
        bp_class = [];
        rms_class = [];

        % loop through each segment of data in the data file
        while segment+f+250 < data_row
            counter = counter + 1;
            fprintf('Classifying segment: %d\n', counter)
            bp_values = [];
            rms_values = [];

            % loop through each channel in the data
            for channel = 2:(last_channel)
                eeg_channel_data = data(segment+1:segment+f+250, channel);

                % pass channel data through a bandpass filter
                alpha_bandpass = bandpass(eeg_channel_data, [8 13], f);
                beta_bandpass = bandpass(eeg_channel_data, [13 32], f);

                %
                for x = 1:5
                    alpha_bandpass(1, :) = [];
                    alpha_bandpass(end, :) = [];
                    beta_bandpass(1, :) = [];
                    beta_bandpass(end, :) = [];
                    x = x + 1;
                end

                % get bandpower and rms values
                alpha_bp = bandpower(alpha_bandpass);
                beta_bp = bandpower(beta_bandpass);
                alpha_rms = rms(alpha_bandpass);
                beta_rms = rms(beta_bandpass);

                % assign bp and rms values
                bp_values(end+1) = alpha_bp/beta_bp;
                rms_values(end+1) = alpha_rms/beta_rms;
            end

            if  last_channel == 9
                [bp_class_interim] = BP_classification_cyton(bp_values);
                [rms_class_interim] = RMS_classification_cyton(rms_values);
            else
                [bp_class_interim] = BP_classification(bp_values);
                [rms_class_interim] = RMS_classification(rms_values);
            end

            bp_class_interim = bp_class_interim;
            rms_class_interim = rms_class_interim;
            bp_class = [bp_class, bp_class_interim]
            rms_class = [rms_class, rms_class_interim]

            segment = segment + 500;
        end
    end

