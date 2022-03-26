function preprocessing
    dirty_cyton_data=readmatrix('mateo_2sec_for_testing.txt'); %File type here could be a csv,txt or xlsx file
%Raw Data coming from cyton has the following columns:
    time_data=dirty_cyton_data(:,1);
    attention_channel_ch1=dirty_cyton_data(:,2);
    dirty_cyton_data_ch2=dirty_cyton_data(:,3);
    dirty_cyton_data_ch3=dirty_cyton_data(:,4);
    dirty_cyton_data_ch4=dirty_cyton_data(:,5);
    dirty_cyton_data_ch5=dirty_cyton_data(:,6);
    dirty_cyton_data_ch6=dirty_cyton_data(:,7);
    dirty_cyton_data_ch7=dirty_cyton_data(:,8);
    reference_channel_ch8=dirty_cyton_data(:,9);

%Re-referencing all channels except the attention channel:
    clean_cyton_data_ch2=dirty_cyton_data_ch2-reference_channel_ch8;
    clean_cyton_data_ch3=dirty_cyton_data_ch3-reference_channel_ch8;
    clean_cyton_data_ch4=dirty_cyton_data_ch4-reference_channel_ch8;
    clean_cyton_data_ch5=dirty_cyton_data_ch5-reference_channel_ch8;
    clean_cyton_data_ch6=dirty_cyton_data_ch6-reference_channel_ch8;
    clean_cyton_data_ch7=dirty_cyton_data_ch7-reference_channel_ch8;


    preprocessing=[time_data attention_channel_ch1 clean_cyton_data_ch2 clean_cyton_data_ch3 clean_cyton_data_ch4 clean_cyton_data_ch5 clean_cyton_data_ch6 clean_cyton_data_ch7 reference_channel_ch8];
    writematrix(preprocessing,'clean_cyton_data.csv')

%Pass attention channel in preprocessed data to the bandpass filtering
    EEG=clean_cyton_data_ch2
    
    apass= bandpass(EEG,[8 13], 200);
    bpass= bandpass(EEG,[13 32], 200);
    l=length(EEG); % finging lenth of data
    t=(0:l-1)*1/200; %calcuating time
    markers=dirty_cyton_data(:,end)*1E-5;
    %% plots
    close all
    tiledlayout(2,2)
    nexttile
    hold on
    plot(t,EEG);
    plot(t,markers);
    title('EEG raw Data');
    xlabel('time (s)');
    ylabel('EEG Amplitude (uV)');
    legend("EEG","Marker");
    hold off
    nexttile
    plot(t,apass,'r');
    title('EEG Alpha Data');
    xlabel('time (s)');
    ylabel('EEG Amplitude (uV)');
    nexttile
    plot(t,bpass,'c');
    title('EEG Beta Data');
    xlabel('time (s)');
    ylabel('EEG Amplitude (uV)');
    %Frequency plot
    fs = 200;
    EEG_fft = fft(EEG);
    L = length(EEG_fft);
    f = (0:L-1)*fs/L;
    nexttile
    plot(f,abs(EEG_fft));
    xlabel('Frequency (Hz)')
    ylabel('Amplitude')
    title('Frequency Data')
end