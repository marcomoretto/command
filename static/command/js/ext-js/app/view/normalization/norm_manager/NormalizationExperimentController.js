Ext.define('command.view.normalization.norm_manager.NormalizationExperimentController', {
    extend: 'Ext.app.ViewController',

    alias: 'controller.normalization_experiment_controller',

    onDeleteCondition: function (me) {
        var panel = me.up('normalization_experiment_design');
        var refreshRequest = panel.getRequestObject('select_design_group');
        var designGroupPanel = panel.down('normalization_design_group');
        var cy_panel = panel.down('cy_design');
        var selected = [];
        cy_panel.cy.$(':selected').forEach(function (e) {
            selected.push(e.json().data.id);
        });
        var request = panel.getRequestObject('delete_condition_sample_group');
        request.values = JSON.stringify({
            'condition_id': selected,
            'normalization_experiment_id': designGroupPanel.getSelection()[0].id
        });
        Ext.Ajax.request({
            url: request.view + '/' + request.operation,
            params: request,
            success: function (response) {
                if (command.current.checkHttpResponse(response)) {
                    var cy_panel = panel.down('cy_design');
                    refreshRequest.values = designGroupPanel.getSelection()[0].id;
                    panel.controller.requestDrawDesign(refreshRequest, cy_panel);
                }
            },
            failure: function (response) {
                console.log('Server error', reponse);
            }
        });
    },

    onNewCondition: function (me) {
        var panel = me.up('normalization_experiment_design');
        var designGroupPanel = panel.down('normalization_design_group');
        var cy_panel = panel.down('cy_design');
        var selected = [];
        cy_panel.cy.$(':selected').forEach(function (e) {
            selected.push(e.json().data.id);
        });
        Ext.MessageBox.prompt('Condition name', 'Enter condition name.', function (btn, text) {
            var request = panel.getRequestObject('create_condition_sample_group');
            request.values = JSON.stringify({
                'condition_name': text,
                'samples': selected
            });
            if (btn == 'ok') {
                Ext.Ajax.request({
                    url: request.view + '/' + request.operation,
                    params: request,
                    success: function (response) {
                        if (command.current.checkHttpResponse(response)) {
                            var refreshRequest = panel.getRequestObject('select_design_group');
                            var cy_panel = panel.down('cy_design');
                            refreshRequest.values = designGroupPanel.getSelection()[0].id;
                            panel.controller.requestDrawDesign(refreshRequest, cy_panel);
                        }
                    },
                    failure: function (response) {
                        console.log('Server error', reponse);
                    }
                });
            }
        });
    },

    onUpdateNormalizationDesignGroup: function(me) {
        var panel = me.up('#normalization_design_group');
        Ext.MessageBox.prompt('Update group name', 'Enter new sample group name.', function (btn, text) {
            var request = panel.getRequestObject('update_sample_group');
            request.values = JSON.stringify({
                'group_id': panel.getSelection()[0].id,
                'group_name': text
            });
            if (btn == 'ok') {
                Ext.Ajax.request({
                    url: request.view + '/' + request.operation,
                    params: request,
                    success: function (response) {
                        command.current.checkHttpResponse(response);
                    },
                    failure: function (response) {
                        console.log('Server error', reponse);
                    }
                });
            }
        });
    },

    onRemoveSample: function (me, idx) {
        var panel = me.up('normalization_experiment_design');
        var designGroupPanel = panel.down('#normalization_design_group');
        var request = panel.getRequestObject('delete_sample_from_group');
        var item = me.store.data.items[idx];
        request.values = item.id;
        Ext.Ajax.request({
            url: request.view + '/' + request.operation,
            params: request,
            success: function (response) {
                if (command.current.checkHttpResponse(response)) {
                    var refreshRequest = panel.getRequestObject('select_design_group');
                    var cy_panel = panel.down('cy_design');
                    refreshRequest.values = designGroupPanel.getSelection()[0].id;
                    panel.controller.requestDrawDesign(refreshRequest, cy_panel);
                }
            },
            failure: function (response) {
                console.log('Server error', reponse);
            }
        })
    },

    onUninkConditions: function(me) {
        var panel = me.up('normalization_experiment_design');
        var cy_panel = panel.down('cy_design');
        var designGroupPanel = panel.down('normalization_design_group');
        var request = panel.getRequestObject('unlink_conditions');
        var edges = [];
        cy_panel.cy.$(':selected').forEach(function (e, i) {
            edges.push(e.json().data.id);
        });
        request.values = JSON.stringify({
            'edges': edges,
            'normalization_experiment_id': designGroupPanel.getSelection()[0].id
        });
        Ext.Ajax.request({
            url: request.view + '/' + request.operation,
            params: request,
            success: function (response) {
                if (command.current.checkHttpResponse(response)) {
                    var request = designGroupPanel.getRequestObject('select_design_group');
                    request.values = designGroupPanel.getSelection()[0].id;
                    panel.controller.requestDrawDesign(request, cy_panel);
                }
            },
            failure: function (response) {
                console.log('Server error', reponse);
            }
        });
    },

    onLinkConditions: function(me) {
        var panel = me.up('normalization_experiment_design');
        var cy_panel = panel.down('cy_design');
        var designGroupPanel = panel.down('normalization_design_group');
        var request = panel.getRequestObject('link_conditions');
        request.values = JSON.stringify({
            'nodes': cy_panel.cy.selected_nodes_order,
            'normalization_experiment_id': designGroupPanel.getSelection()[0].id
        });
        Ext.Ajax.request({
            url: request.view + '/' + request.operation,
            params: request,
            success: function (response) {
                if (command.current.checkHttpResponse(response)) {
                    var request = designGroupPanel.getRequestObject('select_design_group');
                    request.values = designGroupPanel.getSelection()[0].id;
                    panel.controller.requestDrawDesign(request, cy_panel);
                }
            },
            failure: function (response) {
                console.log('Server error', reponse);
            }
        });
    },

    onDeleteNormalizationDesignGroup: function(me) {
        var panel = me.up('#normalization_design_group');
        var cy_panel = panel.up('normalization_experiment').down('cy_design');
        Ext.MessageBox.show({
            title: 'Remove sample group',
            msg: 'Are you sure you want to remove this sample group?',
            buttons: Ext.MessageBox.YESNOCANCEL,
            icon: Ext.MessageBox.QUESTION,
            fn: function (a) {
                if (a == 'yes') {
                    var request = panel.getRequestObject('remove_normalization_design_group');
                    request.values = panel.getSelection()[0].id;
                    Ext.Ajax.request({
                        url: request.view + '/' + request.operation,
                        params: request,
                        success: function (response) {
                            if (command.current.checkHttpResponse(response)) {
                                panel.controller.doDrawDesign(cy_panel, []);
                            }
                        },
                        failure: function (response) {
                            console.log('Server error', reponse);
                        }
                    });
                }
            }
        })
    },

    doDrawDesign: function(cy_panel, cy_elements, request) {
        var layout = 'circle';
        if (cy_elements.nodes && cy_elements.nodes.length > 0 && cy_elements.nodes[0].position) {
            layout = 'preset';
        }
        var panel = cy_panel.up('#design_panel');
        var newConditionButton = panel.down('#newConditionButton');
        var deleteConditionButton = panel.down('#deleteConditionButton');
        var linkConditionButton = panel.down('#linkConditionButton');
        var unlinkConditionButton = panel.down('#unlinkConditionButton');
        newConditionButton.setDisabled(true);
        deleteConditionButton.setDisabled(true);
        linkConditionButton.setDisabled(true);
        unlinkConditionButton.setDisabled(true);
        cy_panel.cy = cytoscape({
            container: document.getElementById(cy_panel.id), // container to render in
            elements: cy_elements,
            style: [ // the stylesheet for the graph
                {
                    selector: 'node[type="sample"]',
                    style: {
                        'content': 'data(name)',
                        'text-opacity': 0.8,
                        'text-valign': 'center',
                        'text-halign': 'right',
                        'background-color': 'lightblue',
                        'shape': 'roundrectangle'
                      }
                },
                {
                    selector: 'node[type="condition"]',
                    style: {
                        'content': 'data(name)',
                        'text-opacity': 0.8,
                        'text-valign': 'center',
                        'text-halign': 'right',
                        'background-color': 'lightyellow',
                        'shape': 'roundrectangle'
                      }
                },
                {
                    selector: 'edge',
                    style: {
                        'curve-style': 'bezier',
                        'width': 4,
                        'target-arrow-shape': 'triangle',
                        'line-color': '#9dbaea',
                        'target-arrow-color': '#9dbaea'
                      }
                }
            ],
            layout: {
                name: layout
            },
            boxSelectionEnabled:true
        });
        cy_panel.cy.selected_nodes_order = [];
        cy_panel.cy.on('free', 'node', function(evt){
            if (request) {
                var jsonRequest = JSON.parse(request.values);
                if (jsonRequest.normalization_experiment_id) {
                    request.values = {
                        'normalization_experiment_id': jsonRequest.normalization_experiment_id,
                        'node_positions': []
                    };
                } else {
                    request.values = {
                        'normalization_experiment_id': request.values,
                        'node_positions': []
                    };
                }
                cy_panel.cy.nodes().forEach(function (e, i) {
                    var jsonNode = e.json();
                    request.values.node_positions.push({
                        'node_id': jsonNode.data.id,
                        'position': jsonNode.position
                    });
                });
                request.values = JSON.stringify(request.values);
                Ext.Ajax.request({
                    url: request.view + '/' + request.operation,
                    params: request,
                    success: function (response) {
                        command.current.checkHttpResponse(response);
                    },
                    failure: function (response) {
                        console.log('Server error', reponse);
                    }
                });
            }
        });
        cy_panel.cy.on('select', 'edge', function(evt){
            var panel = cy_panel.up('#design_panel');
            var unlinkConditionButton = panel.down('#unlinkConditionButton');
            evt.target[0].animate({
                'style': {
                    'line-color': 'green',
                    'width': 6,
                    'target-arrow-color': 'green'
                }
            });
            unlinkConditionButton.setDisabled(false);
        });
        cy_panel.cy.on('unselect', 'edge', function(evt){
            var panel = cy_panel.up('#design_panel');
            var unlinkConditionButton = panel.down('#unlinkConditionButton');
            evt.target[0].animate({
                'style': {
                    'line-color': '#9dbaea',
                    'width': 4,
                    'target-arrow-color': '#9dbaea'
                }
            });
            unlinkConditionButton.setDisabled(true);
        });
        cy_panel.cy.on('select', 'node', function(evt){
            var sampleNodes = [];
            var conditionNodes = [];
            cy_panel.cy.$(':selected').forEach(function (e, i) {
                if (e.json().data.type == 'condition') {
                    conditionNodes.push(e.json().data.id);
                } else {
                    sampleNodes.push(e.json().data.id);
                }
            });
            var panel = cy_panel.up('#design_panel');
            var newConditionButton = panel.down('#newConditionButton');
            var deleteConditionButton = panel.down('#deleteConditionButton');
            var linkConditionButton = panel.down('#linkConditionButton');
            var unlinkConditionButton = panel.down('#unlinkConditionButton');
            if (conditionNodes.length > 0) {
                deleteConditionButton.setDisabled(false);
            }
            if (conditionNodes.length == 2) {
                linkConditionButton.setDisabled(false);
            }
            if (sampleNodes.length > 0) {
                newConditionButton.setDisabled(false);
            }
            if (sampleNodes.length > 0) {
                linkConditionButton.setDisabled(true);
            }
            if (evt.target[0]._private.data.type == 'sample') {
                evt.target[0].animate({
                    'style': { 'background-color': 'blue' }
                });
            } else {
                evt.target[0].animate({
                    'style': { 'background-color': 'green' }
                });
            }
            cy_panel.cy.selected_nodes_order.push(evt.target[0].json().data.id);
        });
        cy_panel.cy.on('unselect', 'node', function(evt){
            var index = cy_panel.cy.selected_nodes_order.indexOf(evt.target[0].json().data.id);
            if (index > -1) {
              cy_panel.cy.selected_nodes_order.splice(index, 1);
            }
            var sampleNodes = [];
            var conditionNodes = [];
            cy_panel.cy.$(':selected').forEach(function (e, i) {
                if (e.json().data.type == 'condition') {
                    conditionNodes.push(e.json().data.id);
                } else {
                    sampleNodes.push(e.json().data.id);
                }
            });
            var panel = cy_panel.up('#design_panel');
            var newConditionButton = panel.down('#newConditionButton');
            var deleteConditionButton = panel.down('#deleteConditionButton');
            var linkConditionButton = panel.down('#linkConditionButton');
            newConditionButton.setDisabled(true);
            deleteConditionButton.setDisabled(true);
            linkConditionButton.setDisabled(true);
            if (conditionNodes.length > 0) {
                deleteConditionButton.setDisabled(false);
            }
            if (conditionNodes.length == 2) {
                linkConditionButton.setDisabled(false);
            }
            if (sampleNodes.length > 1) {
                newConditionButton.setDisabled(false);
            }
            if (sampleNodes.length > 0) {
                linkConditionButton.setDisabled(true);
            }
            if (evt.target[0]._private.data.type == 'sample') {
                evt.target[0].animate({
                    'style': { 'background-color': 'lightblue' }
                });
            } else {
                evt.target[0].animate({
                    'style': { 'background-color': 'lightyellow' }
                });
            }
        });
    },

    requestDrawDesign: function(request, cy_panel) {
        var panel = cy_panel.up('normalization_experiment').down('normalization_design_group');
        var positionRequest = JSON.parse(JSON.stringify(request));
        Ext.Ajax.request({
            url: request.view + '/' + request.operation,
            params: request,
            success: function (response) {
                if (command.current.checkHttpResponse(response)) {
                    var reply = JSON.parse(response.responseText);
                    positionRequest.operation = 'update_node_positions';
                    panel.controller.doDrawDesign(cy_panel, reply.design.elements, positionRequest);
                }
            },
            failure: function (response) {
                console.log('Server error', reponse);
            }
        });
    },

    onNormalizationDesignGroupItemClick: function(me, record, item, index, e, eOpts) {
        var panel = me.up('normalization_design_group');
        var request = panel.getRequestObject('select_design_group');
        var cy_panel = panel.up('normalization_experiment_design').down('cy_design');
        request.values = record.id;
        panel.controller.requestDrawDesign(request, cy_panel);
    },

    cyDesignAfterRender: function (me) {

    },

    onNormalizationDesignGroupAfterRender: function (me) {
        var panel = me.up('normalization_experiment');
        var ws = command.current.ws;
        var operation = 'read_normalization_design_group';
        var request = me.getRequestObject(operation);
        request.values = panel.command_params;
        ws.listen();
        ws.demultiplex(request.view, function(action, stream) {
            if (action.request.operation == request.operation) {
                if (me.store) {
                    me.store.getProxy().setData(action.data);
                    console.log(action.data);
                    me.store.loadPage(action.request.page, {
                        start: 0
                    });
                }
            }
            if (action.request.operation == 'refresh') {
                ws.stream(request.view).send(request);
            }
        });
        ws.stream(request.view).send(request);

    },

    onNewSampleGroup: function (me) {
        var panel = me.up('normalization_experiment');
        var grid = me.up('view_experiment_sample_details');
        var samples = [];
        grid.getSelection().forEach(function (e) {
            samples.push(e.id);
        });
        Ext.MessageBox.prompt('Group name', 'Enter sample group name.', function (btn, text) {
            var request = panel.getRequestObject('create_sample_group');
            request.values = JSON.stringify({
                'normalization_experiment_id': panel.normalization_experiment.id,
                'group_name': text,
                'samples': samples
            });
            if (btn == 'ok') {
                Ext.Ajax.request({
                    url: request.view + '/' + request.operation,
                    params: request,
                    success: function (response) {
                        command.current.checkHttpResponse(response);
                    },
                    failure: function (response) {
                        console.log('Server error', reponse);
                    }
                });
            }
        });
    },

    onNormalizationExperimentAfterRender: function(me) {
        var request = me.getRequestObject('get_experiment_details');
        request.values = me.command_params;
        var onNewSampleGroupFunction = me.controller.onNewSampleGroup;
        Ext.Ajax.request({
            url: request.view + '/' + request.operation,
            params: request,
            success: function (response) {
                command.current.checkHttpResponse(response);
                var resp = JSON.parse(response.responseText);
                me.setTitle('Normalize experiment ' + resp.normalization_experiment.experiment.experiment_access_id);
                me.normalization_experiment = resp.normalization_experiment;
                sample = Ext.ComponentManager.create({
                    title: null,
                    xtype: 'view_experiment_sample_details',
                    reference: 'view_experiment_sample_details',
                    alternative_layout: true,
                    experiment: resp.normalization_experiment.experiment.id,
                    selModel: {
                        selType: 'checkboxmodel',
                        mode: 'MULTI',
                        checkOnly: true,
                        allowDeselect: false
                    },
                    columns: [{
                        text: 'ID',
                        flex: 1,
                        sortable: true,
                        dataIndex: 'id'
                    }, {
                        text: 'Name',
                        flex: 2,
                        sortable: true,
                        dataIndex: 'sample_name'
                    }, {
                        text: 'Description',
                        flex: 5,
                        sortable: true,
                        dataIndex: 'description'
                    }],
                    bbar: [{
                        text: null,
                        xtype: 'button',
                        itemId: 'new_sample_group_button',
                        tooltip: {
                            text: 'New sample group'
                        },
                        iconCls: null,
                        glyph: 'xf055',
                        scale: 'medium',
                        listeners: {
                            click: onNewSampleGroupFunction
                        },
                        bind: {
                            disabled: '{!view_experiment_sample_details.selection}'
                        }
                    }]
                });
                me.down('#sample_panel').insert(sample);
            },
            failure: function (response) {
                console.log('Server error', reponse);
            }
        });
    }

});
