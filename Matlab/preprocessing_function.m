function preprocessing_function
    read_file=readmatrix('dirty_cyton_data.csv') %File type here could be a csv,txt or xlsx file
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
end