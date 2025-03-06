clear; clc;

% 시리얼 포트 설정
port = "COM4"; % 아두이노 연결된 포트
baudRate = 1000000; % 아두이노와 동일한 통신 속도
serialObj = serialport(port, baudRate);
configureTerminator(serialObj, "LF"); % 줄바꿈(LF) 기준으로 데이터 읽기
flush(serialObj); % 기존 버퍼 비우기

% 데이터 저장 변수 초기화
bufferSize = 1000; % 표시할 데이터 개수
voltageData = zeros(1, bufferSize); % 원본 데이터 저장
t = 1:bufferSize; % X축 데이터

% 실시간 데이터 수신 및 업데이트 루프
while true
    if serialObj.NumBytesAvailable > 0 % 데이터가 있을 때만 읽기
        data = readline(serialObj); % 한 줄 읽기
        Vout = str2double(data); % 숫자로 변환
        
        if ~isnan(Vout) % 유효한 데이터만 처리
            % 데이터 저장 (FIFO 방식)
            voltageData = [voltageData(2:end), Vout];
            
            % 주파수 분석을 위한 FFT 계산
            n = length(voltageData); % 데이터 길이
            fs = 240; % 샘플링 주파수 (Hz)
            f = fs * (0:(n/2)) / n; % 주파수 벡터 생성s
            Y = fft(voltageData); % FFT 계산
            P2 = abs(Y / n); % 양방향 스펙트럼
            P1 = P2(1:n/2+1); % 단방향 스펙트럼
            P1(2:end-1) = 2 * P1(2:end-1); % 정규화
            
            % 주파수 스펙트럼 플로팅
            figure(1);
            plot(f, P1);
            xlabel('Frequency (Hz)');
            xlim([0, 120]);
            ylabel('Magnitude');
            title('Frequency Spectrum of Raw Signal');
            grid on;
            
            % 실시간으로 그래프 업데이트
            drawnow limitrate;
        end
    end
end
