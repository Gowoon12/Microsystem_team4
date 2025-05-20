% 서버 IP와 포트 설정
IP = '0.0.0.0';
port = 1234;

% TCP/IP 객체 생성
t = tcpip(IP, port, 'NetworkRole', 'server');
fopen(t);
disp('ESP32 connected. Receiving data...');

while true
    if t.BytesAvailable > 0
        data = fgetl(t); % 줄 단위로 읽기
        voltage = str2double(strtrim(data));
        fprintf('Received: %.6f\n', voltage);
    end
    pause(0.001);
end
