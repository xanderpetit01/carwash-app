from flask import Flask, render_template_string
from flask_socketio import SocketIO, emit
from tempmail import EMail
import requests
import time
from bs4 import BeautifulSoup

app = Flask(__name__)
socketio = SocketIO(app)

# Function to wait for a new email
def wait_for_new_email(email_def, timeout=300, poll_interval=10):
    end_time = time.time() + timeout
    initial_msg_ids = set(msg.id for msg in email_def.get_inbox())

    while time.time() < end_time:
        time.sleep(poll_interval)
        current_msg_ids = set(msg.id for msg in email_def.get_inbox())
        new_msg_ids = current_msg_ids - initial_msg_ids

        if new_msg_ids:
            return
    raise TimeoutError("No new email")

def parse_mail(msg, search, format='lxml'):
    soup = BeautifulSoup(msg.body, 'lxml')
    link = None
    for a in soup.find_all('a', href=True):
        if search in a['href']:  # Adjust this condition based on the actual URL pattern
            link = a['href']
            break

    if link:
        return link
    else:
        print("Link not found.")
        exit(1)

@app.route('/')
def index():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Email Output</title>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
        <script type="text/javascript">
            var socket = io.connect('http://' + document.domain + ':' + location.port);

            socket.on('connect', function() {
                console.log('Connected!');
                socket.emit('run_script');
            });

            socket.on('output', function(msg) {
                var outputDiv = document.getElementById('output');
                var newParagraph = document.createElement('p');
                var parsedMsg = parseMessage(msg);
                newParagraph.innerHTML = parsedMsg;
                outputDiv.appendChild(newParagraph);
            });

            function parseMessage(msg) {
                // Regex to find URLs in the message
                var urlRegex = /(https?:\/\/[^\s]+)/g;
                // Replace URLs with clickable links
                return msg.replace(urlRegex, function(url) {
                    return '<a href="' + url + '">' + url + '</a>';
                });
            }
        </script>
    </head>
    <body>
        <h1>Email Output</h1>
        <div id="output"></div>
    </body>
    </html>
    """)

@socketio.on('run_script')
def run_script():
    print("Getting your discount")
    emit('output', "Getting your discount")

    email = EMail()
    emit('output', email.address)

    request_url = "https://prod1.paywashgo.com/pwg-washdepot-zottegem/front-office/customers"
    first_name = "bla"
    last_name = "bla"
    email_address = email.address
    password = "lbjkvhqrlkhjblmkhbmlhj1"
    postal_code = "9620"
    birthday = "12/05/1999"

    post_body = {
        "firstName": first_name,
        "lastName": last_name,
        "email": email_address,
        "password": password,
        "postalCode": postal_code,
        "birthday": birthday
    }

    x = requests.post(request_url, json=post_body)
    emit('output', x.text)

    msg = email.wait_for_message()
    activation_link = parse_mail(msg, "activate")
    emit('output', f"Activation link: {activation_link}")

    activation_id = activation_link.split('/')[-1]
    activation_link = f"https://prod1.paywashgo.com/pwg-washdepot-zottegem/front-office/customers/activate/{activation_id}"
    r = requests.put(activation_link)
    emit('output', r.text)

    wait_for_new_email(email)
    msg = email.wait_for_message()
    discount_link = parse_mail(msg, "voucher")
    emit('output', "CLICK THE LINK BELOW:")
    emit('output', discount_link)

if __name__ == '__main__':
    socketio.run(app, debug=False)
