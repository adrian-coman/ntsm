{{ fullname | escape | underline }}

.. automodule:: {{ fullname }}

    {% block attributes %}
    {% if attributes %}
    .. rubric:: {{ _('Attributes') }}
    .. autosummary::
        :toctree:
    {% for item in attributes %}
        {{ item }}
    {%- endfor %}
    {% endif %}
    {% endblock %}

    {% block functions %}
    {% if functions %}
    .. rubric:: {{ _('Functions') }}
    .. autosummary::
        :nosignatures:
    {% for item in functions %}
        {{ item.split('.')[-1] }}
    {%- endfor %}
    {% endif %}
    {% endblock %}

    {% block classes %}
    {% if classes %}
    .. rubric:: {{ _('Classes') }}
    .. autosummary::
        :nosignatures:
        :template: custom-class.rst
    {% for item in classes %}
        {{ item.split('.')[-1] }}
    {%- endfor %}
    {% endif %}
    {% endblock %}

    {% block exceptions %}
    {% if exceptions %}
    .. rubric:: {{ _('Exceptions') }}
    .. autosummary::
        :toctree:
    {% for item in exceptions %}
        {{ item }}
    {%- endfor %}
    {% endif %}
    {% endblock %}