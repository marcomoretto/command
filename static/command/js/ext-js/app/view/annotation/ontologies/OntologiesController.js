Ext.define('command.view.annotation.ontologies.OntologiesController', {
    extend: 'Ext.app.ViewController',

    alias: 'controller.ontologies_controller',

    onNewOntology: function (me) {
        console.log(me.id);
        var panel = me.up('available_ontologies');
        var cy_panel = me.up('ontologies').down('cy_ontology');
        console.log(panel.id);
        console.log(cy_panel.id);
        var cy = cytoscape({
            container: document.getElementById(cy_panel.id)
        });
        var request = panel.getRequestObject('new_ontology');
        Ext.Ajax.request({
            url: request.view + '/' + request.operation,
            success: function (response) {
                if (command.current.checkHttpResponse(response)) {
                    var resp = JSON.parse(response.responseText);
                    cy = cytoscape({
                        container: document.getElementById(cy_panel.id), // container to render in
                        elements: resp.ontology,
                        style: [ // the stylesheet for the graph
                            {
                                selector: 'node',
                                style: {
                                    'background-color': '#666',
                                    'label': 'data(id)',
                                    'shape': 'roundrectangle'
                                }
                            },
                            {
                                selector: 'edge',
                                style: {
                                    'width': 3,
                                    'line-color': '#ccc',
                                    'target-arrow-color': '#ccc',
                                    'target-arrow-shape': 'triangle'
                                }
                            }
                        ],
                        layout: {
                            name: 'breadthfirst'
                        }
                    });
                    cy.on('click', 'node', function(evt){
                        var node = evt.target;
                        console.log(evt);
                        var tt = new Ext.ToolTip({
                            target: null,
                            html: 'Ciao Ciao',
                            renderTo: cy_panel.id,
                        });
                        tt.on('hide', function() {
                            tt.isDestroyed || tt.destroy.defer(10, tt);
                        });
                        tt.show();
                        tt.setLocalXY([evt.renderedPosition.x + (25 * evt.cy._private.zoom), evt.renderedPosition.y - (25 * evt.cy._private.zoom)])
                    });

                }
            },
            failure: function (response) {
                console.log('Server error', reponse);
            }
        });
    },

    CyOntologyAfterRender: function (me, eOpts) {

    }
});
