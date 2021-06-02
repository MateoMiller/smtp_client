import base64
import os
import random
import socket
import ssl
import json
import string


def request(socket, request):
    socket.send((request + '\n').encode('utf8'))
    recv_data = socket.recv(65535).decode()
    return recv_data


def get_boundary():
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(40))


host_addr = 'smtp.yandex.ru'
port = 465
user_name = 'mateomiller123'
password = 'dunojhfwcaadulch'


def create_message(config):
    boundary = get_boundary()
    attachments = config['attachments']
    text = config['text']
    message = 'From: MateoMiller123@yandex.ru\n'
    message += f'To: {", ".join(config["receivers"])}\n'
    message += f'Subject: {config["subject"]}\n'
    message += 'MIME-Version: 1.0\n'
    if attachments:
        message += f'Content-Type: multipart/mixed; boundary="{boundary}"\n\n\n'
        for attachment in config['attachments']:
            message = add_attachment(message, attachment, boundary)
        if text:
            message = add_plain_text(message, text, boundary)
        message += f'--{boundary}--\n.'
        return message
    elif text:
        return message + f'\n{text}\n.'
    else:
        return message + '.'


def add_plain_text(message, text, boundary):
    message += f'--{boundary}\n'
    message += f'Content-Transfer-Encoding: 8bit\n'
    message += f'Content-Type: text/plain\n'
    message += f'\n{text}\n'
    return message


def get_file_mime_type(name):
    extension = name.split('.')[-1]
    if extension == 'jpg':
        return 'image/jpg'
    elif extension == 'png':
        return 'image/png'
    elif extension == 'pdf':
        return 'application/pdf'
    else:
        return '*/*'


def add_attachment(message, file_name, boundary):
    before = message
    try:
        mime_type = get_file_mime_type(file_name)
        message += f'--{boundary}\n'
        message += (f'Content-Disposition: attachment; \n\tfilename="{file_name}"\n' +
                    f'Content-Transfer-Encoding: base64\n' +
                    f'Content-Type: {mime_type}; \n\tname="{file_name}"\n\n')
        with open(os.path.join('files', file_name), 'rb') as file:
            message += base64.b64encode(file.read()).decode()
        message += '\n'
        return message
    except Exception:
        return before


def main():
    with open('files/config.json', 'rt', encoding='utf8') as file:
        config = json.loads(file.read())
    with open('files/text.txt', 'rt', encoding='utf8') as file:
        config['text'] = file.read()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect((host_addr, port))
        client = ssl.wrap_socket(client)
        print(client.recv(1024))
        print(request(client, 'EHLO mateomiller123'))
        base64login = base64.b64encode(user_name.encode()).decode()

        base64password = base64.b64encode(password.encode()).decode()
        print(request(client, 'AUTH LOGIN'))
        print(request(client, base64login))
        print(request(client, base64password))
        print(request(client, 'MAIL FROM:MateoMiller123@yandex.ru'))
        for receiver in config['receivers']:
            print(request(client, f'RCPT TO: {receiver}'))
        print(request(client, 'DATA'))
        print(request(client, create_message(config)))
        print(request(client, 'QUIT'))


if __name__ == '__main__':
    main()
