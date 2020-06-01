{% block head %} {{ notification.level }} : {{ notification.verb }} {% endblock head %}
{% block body %}
{{ notification.actor }} {{ notification.verb }} {% if notification.target %} for {{ notification.target }}. {% endif %}
{% endblock body %}
