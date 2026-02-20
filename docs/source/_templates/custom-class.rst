{{ objname | escape | underline}}

.. currentmodule:: {{ module }}

.. autoclass:: {{ objname }}
   :members:
   :inherited-members:
   :show-inheritance:
   :no-index:
   

   {% block attributes %}
   {% if attributes %}
   .. rubric:: {{ _('Attributes') }}
   .. autosummary::
      :nosignatures:
   {% for item in attributes %}
      ~{{ objname }}.{{ item }}
   {%- endfor %}
   {% endif %}
   {% endblock %}