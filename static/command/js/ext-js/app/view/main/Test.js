Ext.define('command.view.main.Test', {
    extend: 'Ext.Component',

    xtype: 'test',

    title: 'Test',

    requires: [
        'Ext.panel.Panel',
        'command.view.main.TestController'
    ],

    controller: 'test',

    store: null,

    alias: 'widget.test',

    itemId: 'test',

    reference: 'test',

    viewModel: {},

    html: 'TEST',

    listeners: {
        //
    },

    /*autoEl : {
        tag : "iframe",
        src : "http://localhost:8888/notebooks/test.ipynb"
    },*/

    initComponent: function() {
        this.callParent();
        Ext.Ajax.request({
            url: 'test/test',
            success: function (response) {
                console.log('TEST');
            },
            failure: function (response) {
                Ext.Msg.alert('Server problem', 'Server Problem');
            }
        });
    },

    destroy: function() {
        this.callParent();
    }
});