clear; clc;

% Serial port configuration
port = "COM4"; 
baudRate = 1000000;
serialObj = serialport(port, baudRate);
configureTerminator(serialObj, "LF"); 
flush(serialObj); 

% Initialize variables for data storage
bufferSize = 1000;
voltageData = zeros(1, bufferSize); 
filteredData = zeros(1, bufferSize);
t = 1:bufferSize;

% Low-pass filter setup
fs = 240; % Sampling frequency (Hz)
lowCutoff = 3; % Low-pass filter cutoff frequency (Hz)
order = 2; % Filter order
[b, a] = butter(order, lowCutoff / (fs / 2), 'low');
filterState = zeros(order, 1); 

% Real-time plotting initialization
figure;
hold on;
rawPlot = plot(t, voltageData, 'Color', [0.7 0.7 0.7], 'DisplayName', 'Raw Data'); 
filteredPlot = plot(t, filteredData, 'r', 'LineWidth', 2, 'DisplayName', 'Low-Pass Filtered');
xlabel('Sample');
ylabel('Voltage (V)');
ylim([0, 0.1]);
legend;
grid on;
title('Real-Time Low-Pass Filtering with Peak Size Calculation');

% Peak calculation variables initialization
peakPlot = plot(NaN, NaN, 'bo', 'MarkerFaceColor', 'b', 'DisplayName', 'Peaks');
dcLine = line([1, bufferSize], [NaN, NaN], 'Color', 'g', 'LineStyle', '--', 'DisplayName', 'DC Value');
currentPeriodText = text(10, 0.08, 'Current Period: N/A', 'FontSize', 12);
avgPeriodText = text(10, 0.075, 'Average Period: N/A', 'FontSize', 12);
currentPeakText = text(10, 0.07, 'Current Peak Size: N/A', 'FontSize', 12);
avgPeakText = text(10, 0.065, 'Average Peak Size: N/A', 'FontSize', 12);

% Peak calculation variables
peakIntervals = [];
peakSizes = [];

% CSV file configuration
csvFileName = 'D:\2025\Paper work\2025_Sensor\250220\250304_MATLAB_VER\data\sensor_data_2.csv';
header = {'Time', 'Raw Data', 'Filtered Data', 'DC Value', 'Current Period', 'Average Period', 'Current Peak Size', 'Average Peak Size', 'Status'};
writecell(header, csvFileName);

bufferForWriting = [];
statusUpdateTimer = tic; % Start status update timer

% Status value mapping
statusMapping = containers.Map(...
    {'OK', 'No Signal', 'Weak Signal', 'Slow Signal'}, ...
    {0, 1, 2, 3});

while true
    if serialObj.NumBytesAvailable > 0
        data = readline(serialObj);
        Vout = str2double(data);

        if ~isnan(Vout)
            voltageData = [voltageData(2:end), Vout];
            [filteredSample, filterState] = filter(b, a, Vout, filterState);
            filteredData = [filteredData(2:end), filteredSample];
            rawPlot.YData = voltageData;
            filteredPlot.YData = filteredData;
            dcValue = mean(filteredData);
            set(dcLine, 'YData', [dcValue, dcValue]);

            % Peak calculation / peak definition 
            [peaks, locs] = findpeaks(filteredData, 'MinPeakHeight', 0.02, 'MinPeakDistance', 10, 'MinPeakProminence', 0.001);

            % Update peak data (real-time)
            if ~isempty(peaks)
                set(peakPlot, 'XData', locs, 'YData', peaks);
            end

            % Perform status check every second
            if toc(statusUpdateTimer) >= 1 % if this is too slow or fast, you can change
                currentPeriod = 0;
                avgPeriod = 0;
                currentPeakSize = 0;
                avgPeakSize = 0;
                status = "OK";

                if ~isempty(peaks)
                    peakIntervals = [peakIntervals, diff(locs)];
                    peakSizes = [peakSizes, abs(peaks - dcValue)];
                    currentPeakSize = abs(peaks(end) - dcValue);
                    avgPeakSize = mean(peakSizes);

                    if ~isempty(peakIntervals)
                        currentPeriod = peakIntervals(end) / fs;
                        avgPeriod = mean(peakIntervals) / fs;
                    end

                    % Determine abnormal status
                    if currentPeakSize < 0.005 && currentPeriod > 2
                        status = "No Signal";
                    elseif currentPeakSize < 0.005
                        status = "Weak Signal";
                    elseif currentPeriod > 2
                        status = "Slow Signal";
                    end

                    % Update status every second
                    set(currentPeriodText, 'String', ['Current Period: ', num2str(currentPeriod, '%.4f'), ' s']);
                    set(avgPeriodText, 'String', ['Average Period: ', num2str(avgPeriod, '%.4f'), ' s']);
                    set(currentPeakText, 'String', ['Current Peak Size: ', num2str(currentPeakSize, '%.4f'), ' V']);
                    set(avgPeakText, 'String', ['Average Peak Size: ', num2str(avgPeakSize, '%.4f'), ' V']);
                else
                    status = "No Signal";
                end

                % Convert status to numeric value
                if strcmp(status, "OK")
                    statusValue = statusMapping('OK');
                elseif strcmp(status, "No Signal")
                    statusValue = statusMapping('No Signal');
                elseif strcmp(status, "Weak Signal")
                    statusValue = statusMapping('Weak Signal');
                elseif strcmp(status, "Slow Signal")
                    statusValue = statusMapping('Slow Signal');
                end

                % Output status every second
                if strcmp(status, "OK")
                    fprintf('OK\n');
                else
                    fprintf('Error at %s: %s\n', datestr(now, 'HH:MM:SS'), status);
                end

                statusUpdateTimer = tic; % Reset timer
            end

            % Data storage
            dataToWrite = {t(end), Vout, filteredSample, dcValue, currentPeriod, avgPeriod, currentPeakSize, avgPeakSize, statusValue};
            bufferForWriting = [bufferForWriting; dataToWrite];

            % Save to CSV file every 100 data points
            if size(bufferForWriting, 1) >= 100
                writecell(bufferForWriting, csvFileName, 'WriteMode', 'append');
                bufferForWriting = [];
            end

            % Update real-time plotting (rate limited)
            drawnow limitrate;
        end
    end
end
