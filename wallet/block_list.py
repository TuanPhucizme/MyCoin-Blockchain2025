<h2>Danh sách các block</h2>
{% for block in blocks %}
  <div>
    <strong>Block #{{ block.index }}</strong><br>
    Hash: {{ block.hash }}<br>
    Previous: {{ block.previous_hash }}<br>
    Timestamp: {{ block.timestamp }}<br>
    Nonce: {{ block.nonce }}
  </div>
  <hr>
{% endfor %}
