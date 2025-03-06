clear; clc;

% Serial port setup
port = "COM4"; 
baudRate = 1000000;
serialObj = serialport(port, baudRate);
configureTerminator(serialObj, "LF"); 
flush(serialObj); 

% Initialize data storage variables
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

% Create a mapping for status
statusMapping = containers.Map( ...
    {'OK', 'No Signal', 'Weak Signal', 'Slow Signal'}, ...
    {1, 0, -1, -2} ...
);

% CSV file setup
csvFileName = 'D:\2025\Paper work\2025_Sensor\250220\250304_MATLAB_VER\data\sensor_data_1.csv';
header = {'Time', 'Raw Data', 'Filtered Data', 'DC Value', 'Current Period', 'Average Period', 'Current Peak Size', 'Average Peak Size', 'Status'};
writecell(header, csvFileName);

bufferForWriting = [];

while true
    if serialObj.NumBytesAvailable > 0
        data = readline(serialObj);
        Vout = str2double(data);

        if ~isnan(Vout)
            % Update voltage data with new reading
            voltageData = [voltageData(2:end), Vout];
            [filteredSample, filterState] = filter(b, a, Vout, filterState);
            filteredData = [filteredData(2:end), filteredSample];
            
            % Update plots with new data
            rawPlot.YData = voltageData;
            filteredPlot.YData = filteredData;
            
            % Calculate DC value (mean of filtered data)
            dcValue = mean(filteredData);
            set(dcLine, 'YData', [dcValue, dcValue]);
            
            % Find peaks in filtered data
            [peaks, locs] = findpeaks(filteredData, 'MinPeakHeight', 0.02, 'MinPeakDistance', 10, 'MinPeakProminence', 0.001);

            % Status check and updating
            status = statusMapping('OK');  % Default: OK (1)
            if ~isempty(peaks)
                set(peakPlot, 'XData', locs, 'YData', peaks);
                peakIntervals = [peakIntervals, diff(locs)];
                peakSizes = [peakSizes, abs(peaks - dcValue)];
                currentPeakSize = abs(peaks(end) - dcValue);
                avgPeakSize = mean(peakSizes);

                if ~isempty(peakIntervals)
                    currentPeriod = peakIntervals(end) / fs;
                    avgPeriod = mean(peakIntervals) / fs;
                else
                    currentPeriod = NaN;
                    avgPeriod = NaN;
                end

                % Status evaluation using statusMapping
                if currentPeakSize < 0.005 && currentPeriod > 2
                    status = statusMapping('No Signal');
                elseif currentPeakSize < 0.005
                    status = statusMapping('Weak Signal');
                elseif currentPeriod > 2
                    status = statusMapping('Slow Signal');
                end

                % Output the current status
                if status == statusMapping('OK')
                    fprintf('OK\n');
                elseif status == statusMapping('No Signal')
                    fprintf('Error at %s: No Signal\n', datestr(now, 'HH:MM:SS'));
                elseif status == statusMapping('Weak Signal')
                    fprintf('Error at %s: Weak Signal\n', datestr(now, 'HH:MM:SS'));
                elseif status == statusMapping('Slow Signal')
                    fprintf('Error at %s: Slow Signal\n', datestr(now, 'HH:MM:SS'));
                end

                % Update displayed text for current and average period, peak size
                set(currentPeriodText, 'String', ['Current Period: ', num2str(currentPeriod, '%.4f'), ' s']);
                set(avgPeriodText, 'String', ['Average Period: ', num2str(avgPeriod, '%.4f'), ' s']);
                set(currentPeakText, 'String', ['Current Peak Size: ', num2str(currentPeakSize, '%.4f'), ' V']);
                set(avgPeakText, 'String', ['Average Peak Size: ', num2str(avgPeakSize, '%.4f'), ' V']);
            else
                % No peaks detected
                currentPeriod = NaN;
                avgPeriod = NaN;
                currentPeakSize = NaN;
                avgPeakSize = NaN;
                status = statusMapping('No Signal');  % No Signal (0)
                fprintf('Error at %s: No Signal\n', datestr(now, 'HH:MM:SS'));
            end

            % Prepare data to write to CSV file
            dataToWrite = {t(end), Vout, filteredSample, dcValue, currentPeriod, avgPeriod, currentPeakSize, avgPeakSize, status};
            bufferForWriting = [bufferForWriting; dataToWrite];
            
            % Write data to CSV file every 100 iterations
            if size(bufferForWriting, 1) >= 100
                writecell(bufferForWriting, csvFileName, 'WriteMode', 'append');
                bufferForWriting = [];
            end
            
            drawnow limitrate;
        end
    end
end
