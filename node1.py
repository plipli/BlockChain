from blockchain import *

# Instantiate the Node
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()


@app.route('/mine', methods=['GET'])
def mine():
    # We run the proof of work algorithm to get the next proof...
    last_block = blockchain.last_block
    proof = blockchain.proof_of_work(last_block)

    # We must receive a reward for finding the proof.
    # The sender is "0" to signify that this node has mined a new coin.
    '''
    blockchain.new_transaction(
        sender="0",
        recipient=node_identifier,
        amount=1,
    )
    '''

    # Forge the new Block by adding it to the chain
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': "New Block Mined",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    #return jsonify(response), 200
    return render_template('index.html', response_data=response['message'])


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    if request.method == 'POST':
        sender = request.form.get('sender')
        recipient = request.form.get('recipient')
        amount = request.form.get('amount')

    # Create a new Transaction
    index = blockchain.new_transaction(sender, recipient, amount)

    response = {
        'transactions': blockchain.current_transactions,
        'length': len(blockchain.current_transactions),
    }

    return render_template('index.html', transactions_data=response['transactions'], trans_num=response['length'])

@app.route('/chainview', methods=['GET'])
def full_chain_view():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    trans = {
        'transactions': blockchain.current_transactions,
        'length': len(blockchain.current_transactions),
    }

    return render_template('index.html', chain_data=response['chain'])

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }

    return jsonify(response), 200


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    if request.method == 'POST':
        nodes = [request.form.get('nodes')]

    #values = request.get_json()

    #nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return render_template('index.html', response_data=response)
    #return jsonify(response), 201


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }

    return render_template('index.html', response_data=response['message'])
    #return jsonify(response), 200


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='127.0.0.1', port=port)
    #app.run(host='0.0.0.0', port=port)
