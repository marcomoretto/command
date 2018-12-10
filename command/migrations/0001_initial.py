# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-12-10 12:29
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AdminOptions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('option_name', models.TextField(default='', unique=True)),
                ('option_value', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='AnnotationValue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.TextField(default='True')),
                ('value_type', models.CharField(choices=[('number', 'NUMBER'), ('string', 'STRING'), ('boolean', 'BOOLEAN')], default='boolean', max_length=7)),
            ],
        ),
        migrations.CreateModel(
            name='AssignedFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('script_name', models.TextField(blank=True, null=True)),
                ('input_filename', models.TextField(blank=True, null=True)),
                ('parameters', models.TextField(blank=True, null=True)),
                ('order', models.IntegerField(blank=True, null=True)),
                ('entity_type', models.CharField(choices=[('EXP', 'EXPERIMENT'), ('PLT', 'PLATFORM'), ('SMP', 'SAMPLE')], max_length=3)),
            ],
        ),
        migrations.CreateModel(
            name='BioFeature',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(unique=True)),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='BioFeatureAnnotation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('annotation_value', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='command.AnnotationValue')),
                ('bio_feature', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='command.BioFeature')),
            ],
        ),
        migrations.CreateModel(
            name='BioFeatureFields',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('description', models.TextField()),
                ('feature_type', models.CharField(choices=[('string', 'STRING'), ('float', 'FLOAT')], max_length=6)),
            ],
        ),
        migrations.CreateModel(
            name='BioFeatureFieldsAdmin',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(unique=True)),
                ('description', models.TextField()),
                ('feature_type', models.CharField(choices=[('string', 'STRING'), ('float', 'FLOAT')], max_length=6)),
            ],
        ),
        migrations.CreateModel(
            name='BioFeatureReporter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('description', models.TextField()),
                ('bio_feature', models.ForeignKey(default=1, null=True, on_delete=django.db.models.deletion.CASCADE, to='command.BioFeature')),
            ],
        ),
        migrations.CreateModel(
            name='BioFeatureReporterFields',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(unique=True)),
                ('description', models.TextField()),
                ('feature_type', models.CharField(choices=[('string', 'STRING'), ('float', 'FLOAT')], max_length=6)),
            ],
        ),
        migrations.CreateModel(
            name='BioFeatureReporterFieldsAdmin',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(unique=True)),
                ('description', models.TextField()),
                ('feature_type', models.CharField(choices=[('string', 'STRING'), ('float', 'FLOAT')], max_length=6)),
            ],
        ),
        migrations.CreateModel(
            name='BioFeatureReporterValues',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.TextField()),
                ('bio_feature_reporter', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='command.BioFeatureReporter')),
                ('bio_feature_reporter_field', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='command.BioFeatureReporterFields')),
            ],
        ),
        migrations.CreateModel(
            name='BioFeatureValues',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.TextField()),
                ('bio_feature', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='command.BioFeature')),
                ('bio_feature_field', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='command.BioFeatureFields')),
            ],
        ),
        migrations.CreateModel(
            name='CompendiumDatabase',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('compendium_name', models.TextField()),
                ('compendium_nick_name', models.TextField(unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('html_description', models.TextField(blank=True, null=True)),
                ('db_engine', models.TextField()),
                ('db_user', models.TextField(blank=True, null=True)),
                ('db_password', models.TextField(blank=True, null=True)),
                ('db_port', models.TextField(blank=True, null=True)),
                ('db_host', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CompendiumType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(unique=True)),
                ('description', models.TextField()),
                ('bio_feature_name', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='DataSource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source_name', models.TextField()),
                ('python_class', models.TextField()),
                ('is_local', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Experiment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('organism', models.TextField(blank=True, null=True)),
                ('experiment_access_id', models.TextField(unique=True)),
                ('experiment_name', models.TextField(blank=True, null=True)),
                ('scientific_paper_ref', models.TextField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('comments', models.TextField(blank=True, null=True)),
                ('data_source', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='command.DataSource')),
            ],
        ),
        migrations.CreateModel(
            name='ExperimentSearchResult',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ori_result_id', models.TextField(blank=True, null=True)),
                ('organism', models.TextField(blank=True, null=True)),
                ('experiment_access_id', models.TextField(blank=True, null=True)),
                ('experiment_alternative_access_id', models.TextField(blank=True, null=True)),
                ('n_samples', models.IntegerField(blank=True, null=True)),
                ('experiment_name', models.TextField(blank=True, null=True)),
                ('platform', models.TextField(blank=True, null=True)),
                ('scientific_paper_ref', models.TextField(blank=True, null=True)),
                ('type', models.TextField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('date', models.DateTimeField(blank=True, null=True)),
                ('data_source', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='command.DataSource')),
            ],
        ),
        migrations.CreateModel(
            name='MessageLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.TextField(blank=True, null=True)),
                ('date', models.DateTimeField(auto_now_add=True, null=True)),
                ('message', models.TextField(blank=True, null=True)),
                ('source', models.CharField(choices=[('User', 'USER'), ('System', 'SYSTEM')], max_length=6)),
            ],
        ),
        migrations.CreateModel(
            name='Normalization',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(unique=True)),
                ('date', models.DateTimeField(auto_now_add=True, null=True)),
                ('version', models.TextField(blank=True, null=True)),
                ('is_public', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='NormalizationDesignGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('design', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='NormalizationDesignSample',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('normalization_design', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='command.NormalizationDesignGroup')),
            ],
        ),
        migrations.CreateModel(
            name='NormalizationExperiment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('use_experiment', models.BooleanField(default=True)),
                ('normalization_parameters', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('experiment', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='command.Experiment')),
                ('normalization', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='command.Normalization')),
            ],
        ),
        migrations.CreateModel(
            name='NormalizationType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(unique=True)),
                ('description', models.TextField()),
                ('python_class', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='NormalizedData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.FloatField()),
                ('bio_feature', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='command.BioFeature')),
                ('normalization_design_group', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='command.NormalizationDesignGroup')),
            ],
        ),
        migrations.CreateModel(
            name='Ontology',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('creation_date', models.DateTimeField(blank=True, null=True)),
                ('original_filename', models.TextField(blank=True, null=True)),
                ('is_biofeature', models.BooleanField(default=False)),
                ('is_sample', models.BooleanField(default=False)),
                ('json', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='OntologyEdge',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_directed', models.BooleanField(default=False)),
                ('edge_type', models.TextField(blank=True, db_index=True, null=True)),
                ('json', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('ontology', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='command.Ontology')),
            ],
        ),
        migrations.CreateModel(
            name='OntologyNode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('original_id', models.TextField(db_index=True)),
                ('json', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('ontology', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='command.Ontology')),
            ],
        ),
        migrations.CreateModel(
            name='ParsingBioFeatureReporter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ParsingBioFeatureReporterValues',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bio_feature_reporter_field', models.TextField(blank=True, null=True)),
                ('value', models.TextField(blank=True, null=True)),
                ('bio_feature_reporter', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='command.ParsingBioFeatureReporter')),
            ],
        ),
        migrations.CreateModel(
            name='ParsingExperiment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('organism', models.TextField(blank=True, null=True)),
                ('experiment_access_id', models.TextField(unique=True)),
                ('experiment_name', models.TextField(blank=True, null=True)),
                ('scientific_paper_ref', models.TextField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('experiment_fk', models.PositiveIntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ParsingPlatform',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('platform_access_id', models.TextField(unique=True)),
                ('platform_name', models.TextField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('platform_type', models.TextField(blank=True, null=True)),
                ('platform_fk', models.PositiveIntegerField(blank=True, null=True)),
                ('reporter_platform', models.PositiveIntegerField(blank=True, null=True)),
                ('reporter_platform_imported', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='ParsingRawData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bio_feature_reporter_name', models.TextField(blank=True, null=True)),
                ('value', models.FloatField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ParsingSample',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sample_name', models.TextField(blank=True, null=True, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('reporter_platform', models.PositiveIntegerField(blank=True, null=True)),
                ('reporter_platform_imported', models.BooleanField(default=False)),
                ('sample_fk', models.PositiveIntegerField(blank=True, null=True)),
                ('experiment', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='command.ParsingExperiment')),
                ('platform', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='command.ParsingPlatform')),
            ],
        ),
        migrations.CreateModel(
            name='Platform',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('platform_access_id', models.TextField(unique=True)),
                ('platform_name', models.TextField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('data_source', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='command.DataSource')),
            ],
        ),
        migrations.CreateModel(
            name='PlatformType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('description', models.TextField()),
                ('bio_feature_reporter_name', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='PlatformTypeAdmin',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(unique=True)),
                ('description', models.TextField()),
                ('bio_feature_reporter_name', models.TextField()),
                ('compendium_type', models.ForeignKey(default=1, null=True, on_delete=django.db.models.deletion.CASCADE, to='command.CompendiumType')),
            ],
        ),
        migrations.CreateModel(
            name='RawData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.FloatField(blank=True, null=True)),
                ('bio_feature_reporter', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='command.BioFeatureReporter')),
            ],
        ),
        migrations.CreateModel(
            name='Sample',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sample_name', models.TextField(blank=True, null=True, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('experiment', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='command.Experiment')),
                ('platform', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='platform', to='command.Platform')),
                ('reporter_platform', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reporter_platform', to='command.Platform')),
            ],
        ),
        migrations.CreateModel(
            name='SampleAnnotation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('annotation_value', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='command.AnnotationValue')),
                ('sample', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='command.Sample')),
            ],
        ),
        migrations.CreateModel(
            name='Status',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(unique=True)),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ValueType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(unique=True)),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ViewTask',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task_id', models.TextField(blank=True, null=True)),
                ('operation', models.TextField(blank=True, null=True)),
                ('view', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='viewtask',
            unique_together=set([('operation', 'view')]),
        ),
        migrations.AddField(
            model_name='rawdata',
            name='sample',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='command.Sample'),
        ),
        migrations.AddField(
            model_name='rawdata',
            name='value_type',
            field=models.ForeignKey(blank=True, default=1, null=True, on_delete=django.db.models.deletion.CASCADE, to='command.ValueType'),
        ),
        migrations.AddField(
            model_name='platform',
            name='platform_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='command.PlatformType'),
        ),
        migrations.AddField(
            model_name='platform',
            name='status',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='command.Status'),
        ),
        migrations.AddField(
            model_name='parsingrawdata',
            name='sample',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='command.ParsingSample'),
        ),
        migrations.AddField(
            model_name='parsingbiofeaturereporter',
            name='platform',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='command.ParsingPlatform'),
        ),
        migrations.AddField(
            model_name='ontologyedge',
            name='source',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='ontology_node_source', to='command.OntologyNode'),
        ),
        migrations.AddField(
            model_name='ontologyedge',
            name='target',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='ontology_node_target', to='command.OntologyNode'),
        ),
        migrations.AddField(
            model_name='normalizeddata',
            name='value_type',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='command.ValueType'),
        ),
        migrations.AddField(
            model_name='normalizationdesignsample',
            name='sample',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='command.Sample'),
        ),
        migrations.AddField(
            model_name='normalizationdesigngroup',
            name='normalization_experiment',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='command.NormalizationExperiment'),
        ),
        migrations.AddField(
            model_name='normalization',
            name='normalization_type',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='command.NormalizationType'),
        ),
        migrations.AddField(
            model_name='experimentsearchresult',
            name='status',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='command.Status'),
        ),
        migrations.AddField(
            model_name='experiment',
            name='status',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='command.Status'),
        ),
        migrations.AddField(
            model_name='compendiumdatabase',
            name='compendium_type',
            field=models.ForeignKey(default=1, null=True, on_delete=django.db.models.deletion.CASCADE, to='command.CompendiumType'),
        ),
        migrations.AddField(
            model_name='biofeaturereporterfieldsadmin',
            name='platform_type',
            field=models.ForeignKey(default=1, null=True, on_delete=django.db.models.deletion.CASCADE, to='command.PlatformTypeAdmin'),
        ),
        migrations.AddField(
            model_name='biofeaturereporterfields',
            name='platform_type',
            field=models.ForeignKey(default=1, null=True, on_delete=django.db.models.deletion.CASCADE, to='command.PlatformType'),
        ),
        migrations.AddField(
            model_name='biofeaturereporter',
            name='platform',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='command.Platform'),
        ),
        migrations.AddField(
            model_name='biofeaturefieldsadmin',
            name='compendium_type',
            field=models.ForeignKey(default=1, null=True, on_delete=django.db.models.deletion.CASCADE, to='command.CompendiumType'),
        ),
        migrations.AddField(
            model_name='assignedfile',
            name='experiment',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='command.Experiment'),
        ),
        migrations.AddField(
            model_name='assignedfile',
            name='message_log',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='command.MessageLog'),
        ),
        migrations.AddField(
            model_name='assignedfile',
            name='platform',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='command.Platform'),
        ),
        migrations.AddField(
            model_name='assignedfile',
            name='sample',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='command.Sample'),
        ),
        migrations.AddField(
            model_name='assignedfile',
            name='status',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='command.Status'),
        ),
        migrations.AddField(
            model_name='annotationvalue',
            name='ontology_node',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='command.OntologyNode'),
        ),
        migrations.AddField(
            model_name='annotationvalue',
            name='value_annotation',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='command.AnnotationValue'),
        ),
        migrations.AlterUniqueTogether(
            name='parsingbiofeaturereporter',
            unique_together=set([('name', 'platform')]),
        ),
        migrations.AlterUniqueTogether(
            name='ontologynode',
            unique_together=set([('original_id', 'ontology')]),
        ),
        migrations.AlterUniqueTogether(
            name='ontologyedge',
            unique_together=set([('source', 'target', 'edge_type', 'ontology')]),
        ),
        migrations.AlterUniqueTogether(
            name='biofeaturereportervalues',
            unique_together=set([('bio_feature_reporter', 'bio_feature_reporter_field')]),
        ),
        migrations.AlterUniqueTogether(
            name='biofeaturereporter',
            unique_together=set([('name', 'platform')]),
        ),
        migrations.AlterUniqueTogether(
            name='biofeatureannotation',
            unique_together=set([('bio_feature', 'annotation_value')]),
        ),
    ]
