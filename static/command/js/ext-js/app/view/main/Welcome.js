Ext.define('command.view.welcome.Welcome', {
    extend: 'Ext.panel.Panel',
    title: 'Welcome',
    xtype: 'welcome',

    layout: 'fit',

    items: [{
        xtype: 'panel',
        margin: '10 500 30 100',
        html: '<h1>Hi there,</h1>' +
        '<h4>This is COMMAND the COMpendia MANagement Desktop ... We still need to properly write this part ' +
        'but you can find all the documentation you need at this link. The GitHub repository is here and you ' +
        'might want to start selecting a Compendium from the Option menu and then clicking on the Data ' +
        'Collection menu. </br>Live long and prosper!</h4>',
        layout: 'fit'
    }],

    initComponent: function() {
        this.callParent();
        mainTab = Ext.ComponentQuery.query('#main_tab_panel')[0];
        mainTab.setTitle('Welcome!');
    }
});