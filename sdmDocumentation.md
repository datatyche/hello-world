# Table of contents
1. [Overview](#Overview)
1. [Software components](#Software-components)
1. [Pre-Requisite](#Pre-Requisite)
1. [Data Flow in SDM](#Logical-Data-Flow)
    1. [Data Layers in SDM](#Data-Layer)
    1. [Data Organization in data lake](#Data-Organization)
    1. [Hive Databases](#Hive-Databases)
1. [Configuration Files](#Configuration-Files)
    1. [Param config](#Param-Config)
    1. [Table config](#Table-Config)
    1. [Table Rename config](#Table-Rename-Config)

# Overview <a name="Overview"></a>

We started ingestion 3 years back when we started our big data journey and we had decided the source data will be maintained in a Hadoop based data lake. Since we had to handle different variety of sources and large number of files, need of a framework for batch ingestion became important.

Our Goal: *“**Configuration driven data ingestion, standard way of maintaining data in the lake**”*

The intention of the framework was to provide developers a configuration driven data ingestion into data lake. It also helped to ensure a standard form of organizing data in data lake. The initial version of the framework was built using java based map-reduce code orchestrated by oozie and falcon. The parameters are in xml form. Later we switched from a map-reduce based framework to spark based framework. Need of near real-time ingestion pushed us to look at a stream or a flow processing methods. After various studies, POCs and discussion with platform providers we finalized the use of HDF for ingestion.

**SDM was formed. SDM is built on HDF (Nifi) and Spark on HDP.**

Our New Goal: ***“Contributing to the community and learning in the process”***

# Software components <a name="Software-components"></a>

  - Hortonworks Data Flow 3.0.1
  - Hortonworks Data Platform 2.3.x, 2.4.x, 2.5.x, 2.6.x
  - Java 1.8
  - Spark 2.x

# Pre-Requisite <a name="Pre-Requisite"></a>

  - 1 HDF cluster
  - 1 HDP cluster
  - 1 Scheduler

# Logical Data Flow in SDM <a name="Logical-Data-Flow"></a>
![](media/Dataflow.png)


## Data Layers in SDM <a name="Data-Layer"></a>
The ingestion for data lake built using SDM has 3 stages of data.

  - Landing
      - Data in landing is a *as is copy* of the file received.
  - Storage / Staging
      - Data is validated and structured based on the source schema.
      - Data which does not pass the validation is kept in separate structures.

  - Processed
      - Two different construct of data is maintained in processed layer, mastered and transactional or snapshots.
      - Mastered construct is for data which has less growth from day to day and gets updates on a regular basis. In this process, daily incremental (delta) is combined with previous available full image and new full image is constructed. The inserts and updates are appended; previous copy of the updated record will be logically closed with the end date and deletes are marked. The new image is maintained in partition.
      - Transactional or snapshot construct is for data which gets inserted with a date of the activity and with very less update or deletes or data which gets repeated with daily or monthly or yearly frequency where all record get repeated to reflect the source image as of that date. These are generally appended as dated partition into same table.

## Data Organization in data lake <a name="Data-Organization"></a>

The primary organization of data lake is at source and country combination. Source is a name of a system from which the data is being sourced, and country can be an alphabetic country code or regional or global code.

All databases are in created in hive and the table name constructs is based on the source and country.

## Hive Databases <a name="Hive-Databases"></a>

  - Storage
    - One table per source table – verified data.
    - One table per source + country – invalid data across various source files within a source – country
    - One table per source + country – warn type data across various source files within a source – country
    - One table per source + country – transform errors data across various files within a source – country

  - Open Image
    - One table per source table. All active record where start date as the date on which SDM received it and end date is ‘9999-12-31’

  - Non-Open Image
    - One table per source table. All inactive record where start date as the date on which SDM received it and end date is the date when SDM closed the record. For deleted data one record with delete flag as 1

  - Operational metadata
    - Config history
    - Data dictionary
    - Duplicates
    - Process Metadata
    - Recon
    - Row Counts
    - Row History

*Example:*
```
Source: CoreBanking(crbnk)
Country: India (in)
Source Tables: Customer, Account and Transaction
Primary construct: crbnk_in
```

<table>
<thead>
<tr class="header">
<th><strong>Database</strong></th>
<th><strong>Description</strong></th>
<th><strong>Hive Database</strong></th>
<th><strong>Hive Table</strong></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Storage</td>
<td>Incoming tables</td>
<td>crbnk_in_storage</td>
<td><p>crbnk_in_customer</p>
<p>crbnk_in_account</p>
<p>crbnk_in_transaction</p></td>
</tr>
<tr class="even">
<td>Storage</td>
<td>Invalid records tables</td>
<td>crbnk_in_storage</td>
<td>crbnk_in_invalidtypes</td>
</tr>
<tr class="odd">
<td>Storage</td>
<td>Warning records tables for defaulting</td>
<td>crbnk_in_storage</td>
<td>crbnk_in_warntypes</td>
</tr>
<tr class="even">
<td>Storage</td>
<td>Transformation error records tables for transformation failures</td>
<td>crbnk_in_storage</td>
<td>crbnk_in_xformtypes</td>
</tr>
<tr class="odd">
<td>Open Image</td>
<td>Data tables</td>
<td>crbnk_in_sri_open</td>
<td><p>crbnk_in_customer</p>
<p>crbnk_in_account</p>
<p>crbnk_in_transaction</p></td>
</tr>
<tr class="even">
<td>Non Open Image</td>
<td>Data Tables – closed records</td>
<td>crbnk_in_sri_nonopen</td>
<td><p>crbnk_in_customer</p>
<p>crbnk_in_account</p>
<p>crbnk_in_transaction</p></td>
</tr>
<tr class="odd">
<td>Operation metadata</td>
<td><p>Config history</p>
<p>Data dictionary</p>
<p>Duplicates</p>
<p>Process Metadata</p>
<p>Recon</p>
<p>Row Counts</p>
<p>Row History</p></td>
<td>crbnk_in_ops</td>
<td><p>crbnk_in_config_history</p>
<p>crbnk_in_data_dictionary</p>
<p>crbnk_in_duplicates</p>
<p>crbnk_in_process_metadata</p>
<p>crbnk_in_recon</p>
<p>crbnk_in_rowcounts</p>
<p>crbnk_in_rowhistory</p></td>
</tr>
<tr class="even">
<td>Operation metadata</td>
<td><p>Table dictionary</p>
<p>Column dictionary</p></td>
<td>crbnk_in_common_metadata</td>
<td><p>crbnk_in_tables</p>
<p>crbnk_in_columns</p></td>
</tr>
</tbody>
</table>

# Configuration Files <a name="Configuration-Files"></a>

The SDM requires 3 configuration files per source + country combination.

1.  Param Config
>   Contain parameters at source - country level required by the SDM engine to process the data.

2.  Table Config
>   Contain details on the table/source files in the group the structure of the tables and the details on the recon.

3.  Rename Config
>   Contains details on the alias name which need to be used to map between source file and hive table.

4.  Column Transformation Rules
>   Contains transformation rules configured to convert source data to target form before storing to Hadoop.

## Param Config <a name="Param-Config"></a>

<table>
<thead>
<tr class="header">
<th>Parameter Name</th>
<th>Source System</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Description</td>
<td>Name of the source system like cards, loans, core banking, etc.</td>
</tr>
<tr class="even">
<td>Example</td>
<td>crbnk</td>
</tr>
<tr class="odd">
<td>Xml Tag</td>
<td>edmhdpif.config.source</td>
</tr>
<tr class="even">
<td>Content from Parameter File</td>
<td><p>&lt;property&gt;</p>
<p>&lt;name&gt;edmhdpif.config.source&lt;/name&gt;</p>
<p>&lt;value&gt;crbnk&lt;/value&gt;</p>
<p>&lt;/property&gt;</p></td>
</tr>
</tbody>
</table>

<table>
<thead>
<tr class="header">
<th>Parameter Name</th>
<th>Country</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Description</td>
<td>Short code of the country or region or global(all/glb)</td>
</tr>
<tr class="even">
<td>Example</td>
<td>in - India</td>
</tr>
<tr class="odd">
<td>Xml Tag</td>
<td>edmhdpif.config.country</td>
</tr>
<tr class="even">
<td>Content from Parameter File</td>
<td><p>&lt;property&gt;</p>
<p>&lt;name&gt;edmhdpif.config.country&lt;/name&gt;</p>
<p>&lt;value&gt;in&lt;/value&gt;</p>
<p>&lt;/property&gt;</p></td>
</tr>
</tbody>
</table>

<table>
<thead>
<tr class="header">
<th>Parameter Name</th>
<th>Source type</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Description</td>
<td>Type of data received from source, CDC – for IBM CDC based replication, BATCH_DELIMITED for delimited batch file, BATCH_FIXEDWIDTH for fixed width file from Mainframe system.</td>
</tr>
<tr class="even">
<td>Example</td>
<td>CDC (CDC / BATCH_DELIMITED / BATCH_FIXEDWIDTH)</td>
</tr>
<tr class="odd">
<td>Xml Tag</td>
<td>edmhdpif.config.sourcing.type</td>
</tr>
<tr class="even">
<td>Content from Parameter File</td>
<td><p>&lt;property&gt;</p>
<p>&lt;name&gt;edmhdpif.config.sourcing.type&lt;/name&gt;</p>
<p>&lt;value&gt;CDC&lt;/value&gt;</p>
<p>&lt;/property&gt;</p></td>
</tr>
</tbody>
</table>

<table>
<thead>
<tr class="header">
<th>Parameter Name</th>
<th>Incoming File Delimiter</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Description</td>
<td>Delimiter for Incoming file applicable for CDC and BATCH_DELIMITED, the delimiter can be any provided the data will not get the delimiter as part of the text. (comma, pipe, ^ , $ )</td>
</tr>
<tr class="even">
<td>Example</td>
<td>/u0001 for Control + A delimiter</td>
</tr>
<tr class="odd">
<td>Xml Tag</td>
<td>edmhdpif.config.filedelimiter</td>
</tr>
<tr class="even">
<td>Content from Parameter File</td>
<td><p>&lt;property&gt;</p>
<p>&lt;name&gt;edmhdpif.config.filedelimiter&lt;/name&gt;</p>
<p>&lt;value&gt;\u0001&lt;/value&gt;</p>
<p>&lt;/property&gt;</p></td>
</tr>
</tbody>
</table>

<table>
<thead>
<tr class="header">
<th>Parameter Name</th>
<th>Source File Incoming Location</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Description</td>
<td>The Path in which the incoming files from source system will be made available for the Nifi to pick up the same.</td>
</tr>
<tr class="even">
<td>Example</td>
<td>/sdm/data/crbnk/in/incoming</td>
</tr>
<tr class="odd">
<td>Xml Tag</td>
<td>edmhdpif.config.source.nfs.location</td>
</tr>
<tr class="even">
<td>Content from Parameter File</td>
<td><p>&lt;property&gt;</p>
<p>&lt;name&gt;edmhdpif.config.source.nfs.location&lt;/name&gt;</p>
<p>&lt;value&gt;/sdm/data/crbnk/in&lt;/value&gt;</p>
<p>&lt;/property&gt;</p></td>
</tr>
</tbody>
</table>

<table>
<thead>
<tr class="header">
<th>Parameter Name</th>
<th>Source File Archive Location in HDFS</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Description</td>
<td>The Path in HDFS where the incoming files are preserved, this is the landing area.</td>
</tr>
<tr class="even">
<td>Example</td>
<td>/data/hadoop/crbnk/in/incoming</td>
</tr>
<tr class="odd">
<td>Xml Tag</td>
<td>edmhdpif.config.source.landing.location</td>
</tr>
<tr class="even">
<td>Content from Parameter File</td>
<td><p>&lt;property&gt;</p>
<p>&lt;name&gt;edmhdpif.config.source.landing.location&lt;/name&gt;</p>
<p>&lt;value&gt;/data/hadoop/crbnk/in/incoming&lt;/value&gt;</p>
<p>&lt;/property&gt;</p></td>
</tr>
</tbody>
</table>

<table>
<thead>
<tr class="header">
<th>Parameter Name</th>
<th>HDFS Parent Dir<strong> </strong></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Description</td>
<td>The Base directory in HDFS where landing, storage and processed data is stored.</td>
</tr>
<tr class="even">
<td>Example</td>
<td>/data/hadoop/crbnk/in</td>
</tr>
<tr class="odd">
<td>Xml Tag</td>
<td>edmhdpif.config.hdfs.data.parent.dir</td>
</tr>
<tr class="even">
<td>Content from Parameter File</td>
<td><p>&lt;property&gt;</p>
<p>&lt;name&gt;edmhdpif.config.hdfs.data.parent.dir&lt;/name&gt;</p>
<p>&lt;value&gt;/data/hadoop/crbnk/in&lt;/value&gt;</p>
<p>&lt;/property&gt;</p></td>
</tr>
</tbody>
</table>

<table>
<thead>
<tr class="header">
<th>Parameter Name</th>
<th>HDFS Temp Folder<strong> </strong></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Description</td>
<td>The temp folder in hdfs for the SDM engine.</td>
</tr>
<tr class="even">
<td>Example</td>
<td>/data/tmp/</td>
</tr>
<tr class="odd">
<td>Xml Tag</td>
<td>edmhdpif.config.hdfs.tmpdir</td>
</tr>
<tr class="even">
<td>Content from Parameter File</td>
<td><p>&lt;property&gt;</p>
<p>&lt;name&gt;edmhdpif.config.hdfs.tmpdir&lt;/name&gt;</p>
<p>&lt;value&gt;/tmp/&lt;/value&gt;</p>
<p>&lt;/property&gt;</p></td>
</tr>
</tbody>
</table>

<table>
<thead>
<tr class="header">
<th>Parameter Name</th>
<th>HDFS XML Path<strong> </strong></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Description</td>
<td>The name and path in HDFS where the table config xml is placed.</td>
</tr>
<tr class="even">
<td>Example</td>
<td>/data/hadoop/fwconfig/crbnk_in_tables_config.xml</td>
</tr>
<tr class="odd">
<td>Xml Tag</td>
<td>edmhdpif.config.hdfs.tableconfig.xml.path</td>
</tr>
<tr class="even">
<td>Content from Parameter File</td>
<td><p>&lt;property&gt;</p>
<p>&lt;name&gt;edmhdpif.config.hdfs.tableconfig.xml.path&lt;/name&gt;</p>
<p>&lt;value&gt;/data/hadoop/fwconfig/crbnk_in_tables_config.xml&lt;/value&gt;</p>
<p>&lt;/property&gt;</p></td>
</tr>
</tbody>
</table>

<table>
<thead>
<tr class="header">
<th>Parameter Name</th>
<th>Storage Schema Name</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Description</td>
<td>The Hive database name for the storage schema. This is the database where verified image, invalid type, warn type and transform errors are recorded.</td>
</tr>
<tr class="even">
<td>Example</td>
<td>crbnk_in_storage</td>
</tr>
<tr class="odd">
<td>Xml Tag</td>
<td>edmhdpif.config.storage.schema</td>
</tr>
<tr class="even">
<td>Content from Parameter File</td>
<td><p>&lt;property&gt;</p>
<p>&lt;name&gt;edmhdpif.config.storage.schema&lt;/name&gt;</p>
<p>&lt;value&gt;crbnk_in_storage&lt;/value&gt;</p>
<p>&lt;/property&gt;</p></td>
</tr>
</tbody>
</table>

<table>
<thead>
<tr class="header">
<th>Parameter Name</th>
<th>Storage Partition Type</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Description</td>
<td>The Storage has ability to store data in intraday frequency partitions and daily storage partition. Allowed parameters are H:H – Hourly files and Hourly Partition, H:D – Hourly files and daily partition and D:D – Daily data and Daily partitions.</td>
</tr>
<tr class="even">
<td>Example</td>
<td>H:D</td>
</tr>
<tr class="odd">
<td>Xml Tag</td>
<td>edmhdpif.config.storage.partition.type</td>
</tr>
<tr class="even">
<td>Content from Parameter File</td>
<td><p>&lt;property&gt;</p>
<p>&lt;name&gt;edmhdpif.config.storage.partition.type&lt;/name&gt;</p>
<p>&lt;value&gt;H:D&lt;/value&gt;</p>
<p>&lt;/property&gt;</p></td>
</tr>
</tbody>
</table>

<table>
<thead>
<tr class="header">
<th>Parameter Name</th>
<th>Processed Data Open Record Schema</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Description</td>
<td>The Hive database name where the tables with open records are created. This is under the processed data.&lt;Source&gt;_&lt;Country&gt;_sri_open is the pattern.</td>
</tr>
<tr class="even">
<td>Example</td>
<td>crbnk_in_sri_open</td>
</tr>
<tr class="odd">
<td>Xml Tag</td>
<td>edmhdpif.config.sri.open.schema</td>
</tr>
<tr class="even">
<td>Content from Parameter File</td>
<td><p>&lt;property&gt;</p>
<p>&lt;name&gt;edmhdpif.config.sri.open.schema&lt;/name&gt;</p>
<p>&lt;value&gt;crbnk_in_sri_open&lt;/value&gt;</p>
<p>&lt;/property&gt;</p></td>
</tr>
</tbody>
</table>

<table>
<thead>
<tr class="header">
<th>Parameter Name</th>
<th>Processed Data Closed Record Schema</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Description</td>
<td>The Hive database name where the tables with closed records are created. This is under the processed data. &lt;Source&gt;_&lt;Country&gt;_sri_nonopen is the pattern.</td>
</tr>
<tr class="even">
<td>Example</td>
<td>crbnk_in_sri_nonopen</td>
</tr>
<tr class="odd">
<td>Xml Tag</td>
<td>edmhdpif.config.sri.nonopen.schema</td>
</tr>
<tr class="even">
<td>Content from Parameter File</td>
<td><p>&lt;property&gt;</p>
<p>&lt;name&gt;edmhdpif.config.sri.nonopen.schema&lt;/name&gt;</p>
<p>&lt;value&gt;crbnk_in_sri_nonopen&lt;/value&gt;</p>
<p>&lt;/property&gt;</p></td>
</tr>
</tbody>
</table>

<table>
<thead>
<tr class="header">
<th>Parameter Name</th>
<th>Operation Schema name</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Description</td>
<td>The Hive database where the tables related to operation metadata are created. The tables are Config history, Data dictionary, Duplicates, Process Metadata, Recon, Row Counts and Row History.</td>
</tr>
<tr class="even">
<td>Example</td>
<td>crbnk_in_ops</td>
</tr>
<tr class="odd">
<td>Xml Tag</td>
<td>edmhdpif.config.ops.schema</td>
</tr>
<tr class="even">
<td>Content from Parameter File</td>
<td><p>&lt;property&gt;</p>
<p>&lt;name&gt;edmhdpif.config.ops.schema&lt;/name&gt;</p>
<p>&lt;value&gt;crbnk_in_ops&lt;/value&gt;</p>
<p>&lt;/property&gt;</p></td>
</tr>
</tbody>
</table>

<table>
<thead>
<tr class="header">
<th>Parameter Name</th>
<th>Input Format</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Description</td>
<td>The Data storage format in the storage area. The data is stored as avro.</td>
</tr>
<tr class="even">
<td>Example</td>
<td>com.databricks.spark.avro</td>
</tr>
<tr class="odd">
<td>Xml Tag</td>
<td>edmhdpif.config.storage.input.format</td>
</tr>
<tr class="even">
<td>Content from Parameter File</td>
<td><p>&lt;property&gt;</p>
<p>&lt;name&gt;edmhdpif.config.storage.input.format&lt;/name&gt;</p>
<p>&lt;value&gt;com.databricks.spark.avro&lt;/value&gt;</p>
<p>&lt;/property&gt;</p></td>
</tr>
</tbody>
</table>

<table>
<thead>
<tr class="header">
<th>Parameter Name</th>
<th>Storage Schema Tables Partition Name</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Description</td>
<td>The column name for the date partition on the tables created in storage schema.</td>
</tr>
<tr class="even">
<td>Example</td>
<td>vds</td>
</tr>
<tr class="odd">
<td>Xml Tag</td>
<td>edmhdpif.config.storage.partition.name</td>
</tr>
<tr class="even">
<td>Content from Parameter File</td>
<td><p>&lt;property&gt;</p>
<p>&lt;name&gt;edmhdpif.config.storage.partition.name&lt;/name&gt;</p>
<p>&lt;value&gt;vds&lt;/value&gt;</p>
<p>&lt;/property&gt;</p></td>
</tr>
</tbody>
</table>

<table>
<thead>
<tr class="header">
<th>Parameter Name</th>
<th>Processed Schema Open Records Table Partition Name</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Description</td>
<td>The column name for the date partition on the tables created under sri open (processed) schema.</td>
</tr>
<tr class="even">
<td>Example</td>
<td>ods</td>
</tr>
<tr class="odd">
<td>Xml Tag</td>
<td>edmhdpif.config.sri.open.partition.name</td>
</tr>
<tr class="even">
<td>Content from Parameter File</td>
<td><p>&lt;property&gt;</p>
<p>&lt;name&gt;edmhdpif.config.sri.open.partition.name&lt;/name&gt;</p>
<p>&lt;value&gt;ods&lt;/value&gt;</p>
<p>&lt;/property&gt;</p></td>
</tr>
</tbody>
</table>

<table>
<thead>
<tr class="header">
<th>Parameter Name</th>
<th>Processed Schema Closed Records Table Partition Name</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Description</td>
<td>The column name for the date partition on the tables created under sri non Open (processed) schema.</td>
</tr>
<tr class="even">
<td>Example</td>
<td>nds</td>
</tr>
<tr class="odd">
<td>Xml Tag</td>
<td>edmhdpif.config.sri.nonopen.partition.name</td>
</tr>
<tr class="even">
<td>Content from Parameter File</td>
<td><p>&lt;property&gt;</p>
<p>&lt;name&gt;edmhdpif.config.sri.nonopen.partition.name&lt;/name&gt;</p>
<p>&lt;value&gt;nds&lt;/value&gt;</p>
<p>&lt;/property&gt;</p></td>
</tr>
</tbody>
</table>

<table>
<thead>
<tr class="header">
<th>Parameter Name</th>
<th>Invalid Types Table Structure</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Description</td>
<td><p>The Structure of Invalid type table.</p>
<table>
<thead>
<tr class="header">
<th>Column Name</th>
<th>Datatype</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Source</td>
<td>Varchar(20)</td>
<td>Source name</td>
</tr>
<tr class="even">
<td>Country</td>
<td>Varchar(10)</td>
<td>Country code</td>
</tr>
<tr class="odd">
<td>Tablename</td>
<td>Varchar(100)</td>
<td>Tablename for which invalid record has been identified</td>
</tr>
<tr class="even">
<td>Data</td>
<td>Varchar(20000)</td>
<td>The entire record from the file.</td>
</tr>
<tr class="odd">
<td>Errormsg</td>
<td>Varchar(2000)</td>
<td>The details error message on the various data attribute</td>
</tr>
<tr class="even">
<td>Ts</td>
<td>Varchar(20)</td>
<td>Timestamp of processing</td>
</tr>
</tbody>
</table></td>
</tr>
<tr class="even">
<td>Example</td>
<td>source VARCHAR(20) ^country VARCHAR(10) ^tablename VARCHAR(100) ^rowid VARCHAR(100) ^data VARCHAR(20000) ^errormsg VARCHAR(20000) ^ts VARCHAR(20)</td>
</tr>
<tr class="odd">
<td>Xml Tag</td>
<td>edmhdpif.config.invalidtypes.schema</td>
</tr>
<tr class="even">
<td>Content from Parameter File</td>
<td><p>&lt;property&gt;</p>
<p>&lt;name&gt;edmhdpif.config.invalidtypes.schema&lt;/name&gt;</p>
<p>&lt;value&gt;source VARCHAR(20) ^country VARCHAR(10) ^tablename VARCHAR(100) ^rowid VARCHAR(100) ^data VARCHAR(20000) ^errormsg VARCHAR(20000) ^ts VARCHAR(20)&lt;/value&gt;</p>
<p>&lt;/property&gt;</p></td>
</tr>
</tbody>
</table>

<table>
<thead>
<tr class="header">
<th>Parameter Name</th>
<th>Warning Types Table Structure</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Description</td>
<td><p>The Structure of Warning type table.</p>
<table>
<thead>
<tr class="header">
<th>Column Name</th>
<th>Datatype</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Source</td>
<td>Varchar(20)</td>
<td>Source name</td>
</tr>
<tr class="even">
<td>Country</td>
<td>Varchar(10)</td>
<td>Country code</td>
</tr>
<tr class="odd">
<td>Tablename</td>
<td>Varchar(100)</td>
<td>Tablename for which invalid record has been identified</td>
</tr>
<tr class="even">
<td>Data</td>
<td>Varchar(20000)</td>
<td>The entire record from the file.</td>
</tr>
<tr class="odd">
<td>Errormsg</td>
<td>Varchar(2000)</td>
<td>The details error message on the various data attribute</td>
</tr>
<tr class="even">
<td>Ts</td>
<td>Varchar(20)</td>
<td>Timestamp of processing</td>
</tr>
</tbody>
</table></td>
</tr>
<tr class="even">
<td>Example</td>
<td>source VARCHAR(20) ^country VARCHAR(10) ^tablename VARCHAR(100) ^rowid VARCHAR(100) ^data VARCHAR(20000) ^errormsg VARCHAR(20000) ^ts VARCHAR(20)</td>
</tr>
<tr class="odd">
<td>Xml Tag</td>
<td>edmhdpif.config.warntypes.schema</td>
</tr>
<tr class="even">
<td>Content from Parameter File</td>
<td><p>&lt;property&gt;</p>
<p>&lt;name&gt;edmhdpif.config.warntypes.schema&lt;/name&gt;</p>
<p>&lt;value&gt;source VARCHAR(20) ^country VARCHAR(10) ^tablename VARCHAR(100) ^rowid VARCHAR(100) ^data VARCHAR(20000) ^errormsg VARCHAR(20000) ^ts VARCHAR(20)&lt;/value&gt;</p>
<p>&lt;/property&gt;</p></td>
</tr>
</tbody>
</table>

<table>
<thead>
<tr class="header">
<th>Parameter Name</th>
<th>Transformation Failures Structure</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Description</td>
<td><p>The Structure of Transform Errors table.</p>
<table>
<thead>
<tr class="header">
<th>Column Name</th>
<th>Datatype</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Source</td>
<td>Varchar(20)</td>
<td>Source name</td>
</tr>
<tr class="even">
<td>Country</td>
<td>Varchar(10)</td>
<td>Country code</td>
</tr>
<tr class="odd">
<td>Tablename</td>
<td>Varchar(100)</td>
<td>Tablename for which invalid record has been identified</td>
</tr>
<tr class="even">
<td>Data</td>
<td>Varchar(20000)</td>
<td>The entire record from the file.</td>
</tr>
<tr class="odd">
<td>Errormsg</td>
<td>Varchar(2000)</td>
<td>The details error message on the various data attribute</td>
</tr>
<tr class="even">
<td>Ts</td>
<td>Varchar(20)</td>
<td>Timestamp of processing</td>
</tr>
</tbody>
</table></td>
</tr>
<tr class="even">
<td>Example</td>
<td>source VARCHAR(20) ^country VARCHAR(10) ^tablename VARCHAR(100) ^rowid VARCHAR(100) ^data VARCHAR(20000) ^errormsg VARCHAR(20000) ^ts VARCHAR(20)</td>
</tr>
<tr class="odd">
<td>Xml Tag</td>
<td>edmhdpif.config.xformfailures.schema</td>
</tr>
<tr class="even">
<td>Content from Parameter File</td>
<td><p>&lt;property&gt;</p>
<p>&lt;name&gt;edmhdpif.config.xformfailures.schema&lt;/name&gt;</p>
<p>&lt;value&gt;source VARCHAR(20) ^country VARCHAR(10) ^tablename VARCHAR(100) ^rowid VARCHAR(100) ^data VARCHAR(20000) ^errormsg VARCHAR(20000) ^ts VARCHAR(20)&lt;/value&gt;</p>
<p>&lt;/property&gt;</p></td>
</tr>
</tbody>
</table>

<table>
<thead>
<tr class="header">
<th>Parameter Name</th>
<th>End of Day Marker Strategy</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Description</td>
<td><p>The method by with SDM engine understands the End of Day process has been completed on source. Current possible methods are GLOBAL_EOD – One file is generated by source where it indicates the time by which the EOD is completed for the source country combination.</p>
<p>TABLE_LEVEL_EOD – One file is generated by source and the file contains all tables sourced and each table has different time of EOD.</p>
<p>GLOBAL_EOD_TIME_TRIGGERED – Source does not send any EOD indication SDM needs to generate a system generated EOD at a specific time daily.</p>
<p>GLOBAL_EOD_FUNCTION - One file is generated by source where it indicates the time by which the EOD is completed for the source country combination. Source sends multiple records and SDM need to search for a specific combination of data to identify the EOD.</p>
<p>FILE_BY_FILE – This type of processing is applicable for batch based files, there is no EOD indication from source. After receipt of every file the file needs to be processed immediately.</p>
<p>AFTER_ALL_FILE – This type of processing is applicable for batch based files, there is no EOD indication from source. After receipt of all the files from source the files will be processed.</p></td>
</tr>
<tr class="even">
<td>Example</td>
<td>GLOBAL_EOD</td>
</tr>
<tr class="odd">
<td>Xml Tag</td>
<td>edmhdpif.config.eod.marker.strategy</td>
</tr>
<tr class="even">
<td>Content from Parameter File</td>
<td><p>&lt;property&gt;</p>
<p>&lt;name&gt;edmhdpif.config.eod.marker.strategy&lt;/name&gt;</p>
<p>&lt;value&gt;GLOBAL_EOD&lt;/value&gt;</p>
<p>&lt;/property&gt;</p></td>
</tr>
</tbody>
</table>

<table>
<thead>
<tr class="header">
<th>Parameter Name</th>
<th>EOD Marker Trigger Time</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Description</td>
<td>Applicable for - GLOBAL_EOD_TIME_TRIGGERED SDM will be automatically generating EOD file at this time</td>
</tr>
<tr class="even">
<td>Example</td>
<td>23:55:00</td>
</tr>
<tr class="odd">
<td>Xml Tag</td>
<td>edmhdpif.config.eod.marker.trigger_time</td>
</tr>
<tr class="even">
<td>Content from Parameter File</td>
<td><p>&lt;property&gt;</p>
<p>&lt;name&gt; edmhdpif.config.eod.marker.trigger_time &lt;/name&gt;</p>
<p>&lt;value&gt;23:55:00&lt;/value&gt;</p>
<p>&lt;/property&gt;</p></td>
</tr>
</tbody>
</table>

<table>
<thead>
<tr class="header">
<th>Parameter Name</th>
<th>EOD Trigger File Name</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Description</td>
<td>The File name by with SDM will identify that the EOD has been completed and the EOD processing on SDM will be initiated.</td>
</tr>
<tr class="even">
<td>Example</td>
<td>Eodfile</td>
</tr>
<tr class="odd">
<td>Xml Tag</td>
<td>edmhdpif.config.sri.job.trigger.file.pattern</td>
</tr>
<tr class="even">
<td>Content from Parameter File</td>
<td><p>&lt;property&gt;</p>
<p>&lt;name&gt;edmhdpif.config.sri.job.trigger.file.pattern&lt;/name&gt;</p>
<p>&lt;value&gt;eodfile&lt;/value&gt;</p>
<p>&lt;/property&gt;</p></td>
</tr>
</tbody>
</table>

<table>
<thead>
<tr class="header">
<th>Parameter Name</th>
<th>Status File Location</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Description</td>
<td>The path in which the status files during batch will be written by SDM this will be used by the scheduler to pickup the status and updated the pert accordingly.</td>
</tr>
<tr class="even">
<td>Example</td>
<td>/data/status/crbnk/in/</td>
</tr>
<tr class="odd">
<td>Xml Tag</td>
<td>edmhdpif.config.statusfile.location</td>
</tr>
<tr class="even">
<td>Content from Parameter File</td>
<td><p>&lt;property&gt;</p>
<p>&lt;name&gt;edmhdpif.config.statusfile.location&lt;/name&gt;</p>
<p>&lt;value&gt;/data/status/crbnk/in/&lt;/value&gt;</p>
<p>&lt;/property&gt;</p></td>
</tr>
</tbody>
</table>

<table>
<thead>
<tr class="header">
<th>Parameter Name</th>
<th>Recon Table Name</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Description</td>
<td>The table / file where the source had populated the record counts and checksum of the tables post the EOD and before the subsequent posting starts for next day.</td>
</tr>
<tr class="even">
<td>Example</td>
<td>cdc_recon_val</td>
</tr>
<tr class="odd">
<td>Xml Tag</td>
<td>edmhdpif.config.recon.tablename</td>
</tr>
<tr class="even">
<td>Content from Parameter File</td>
<td><p>&lt;property&gt;</p>
<p>&lt;name&gt;edmhdpif.config.recon.tablename&lt;/name&gt;</p>
<p>&lt;value&gt;cdc_recon_val&lt;/value&gt;</p>
<p>&lt;/property&gt;</p></td>
</tr>
</tbody>
</table>

<table>
<thead>
<tr class="header">
<th>Parameter Name</th>
<th>Recon Table Column Position for Table Name</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Description</td>
<td>The column position of the table name in the recon file, starting index is 0.</td>
</tr>
<tr class="even">
<td>Example</td>
<td>If the recon file has 10 columns and 5<sup>th</sup> column has the tablename then the index is 4.</td>
</tr>
<tr class="odd">
<td>Xml Tag</td>
<td>edmhdpif.config.recon.tablename.colnum</td>
</tr>
<tr class="even">
<td>Content from Parameter File</td>
<td><p>&lt;property&gt;</p>
<p>&lt;name&gt;edmhdpif.config.recon.tablename.colnum&lt;/name&gt;</p>
<p>&lt;value&gt;10&lt;/value&gt;</p>
<p>&lt;/property&gt;</p></td>
</tr>
</tbody>
</table>

<table>
<thead>
<tr class="header">
<th>Parameter Name</th>
<th>Recon Table Column Position for Table Count</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Description</td>
<td>The column position of table count in the recon file, starting index is 0.</td>
</tr>
<tr class="even">
<td>Example</td>
<td>If the recon file has 10 columns and 6<sup>th</sup> column has the table count, then the index is 5.</td>
</tr>
<tr class="odd">
<td>Xml Tag</td>
<td>edmhdpif.config.recon.tablecount.colnum</td>
</tr>
<tr class="even">
<td>Content from Parameter File</td>
<td><p>&lt;property&gt;</p>
<p>&lt;name&gt;edmhdpif.config.recon.tablecount.colnum&lt;/name&gt;</p>
<p>&lt;value&gt;11&lt;/value&gt;</p>
<p>&lt;/property&gt;</p></td>
</tr>
</tbody>
</table>

<table>
<thead>
<tr class="header">
<th>Parameter Name</th>
<th>Recon Table Directory</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Description</td>
<td>SDM will generate the recon results in the specified path.</td>
</tr>
<tr class="even">
<td>Example</td>
<td>/data/target/recon/crbnk/in/</td>
</tr>
<tr class="odd">
<td>Xml Tag</td>
<td>edmhdpif.config.recon.tabledir</td>
</tr>
<tr class="even">
<td>Content from Parameter File</td>
<td><p>&lt;property&gt;</p>
<p>&lt;name&gt;edmhdpif.config.recon.tabledir&lt;/name&gt;</p>
<p>&lt;value&gt;/data/target/recon/crbnk/in/&lt;/value&gt;</p>
<p>&lt;/property&gt;</p></td>
</tr>
</tbody>
</table>

<table>
<thead>
<tr class="header">
<th>Parameter Name</th>
<th>Framework Configuration Path</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Description</td>
<td>Path where the config files are placed by SDM deployment.</td>
</tr>
<tr class="even">
<td>Example</td>
<td>/data/Hadoop/crbnk/in/hdata/config/</td>
</tr>
<tr class="odd">
<td>Xml Tag</td>
<td>edmhdpif.config.fw.config.path</td>
</tr>
<tr class="even">
<td>Content from Parameter File</td>
<td><p>&lt;property&gt;</p>
<p>&lt;name&gt;edmhdpif.config.fw.config.path&lt;/name&gt;</p>
<p>&lt;value&gt;/data/Hadoop/crbnk/in/hdata/config/&lt;/value&gt;</p>
<p>&lt;/property&gt;</p></td>
</tr>
</tbody>
</table>

<table>
<thead>
<tr class="header">
<th>Parameter Name</th>
<th>Common Metadata Schema</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Description</td>
<td>The database in hive where the tables and columns for the tables are stored for the source and country pair.</td>
</tr>
<tr class="even">
<td>Example</td>
<td>crbnk_in_common_metadata</td>
</tr>
<tr class="odd">
<td>Xml Tag</td>
<td>edmhdpif.config.commonmetadata.schema</td>
</tr>
<tr class="even">
<td>Content from Parameter File</td>
<td><p>&lt;property&gt;</p>
<p>&lt;name&gt;edmhdpif.config.commonmetadata.schema&lt;/name&gt;</p>
<p>&lt;value&gt;${edmhdpif.config.source}_common_metadata&lt;/value&gt;</p>
<p>&lt;/property&gt;</p></td>
</tr>
</tbody>
</table>

<table>
<thead>
<tr class="header">
<th>Parameter Name</th>
<th>File Incoming Location</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Description</td>
<td>Incoming location where the source files will be made available.</td>
</tr>
<tr class="even">
<td>Example</td>
<td>/data/sdm/crbnk/in/incoming</td>
</tr>
<tr class="odd">
<td>Xml Tag</td>
<td>edmhdpif.config.source.nfs.location</td>
</tr>
<tr class="even">
<td>Content from Parameter File</td>
<td><p>&lt;property&gt;</p>
<p>&lt;name&gt;edmhdpif.config.source.nfs.location&lt;/name&gt;</p>
<p>&lt;value&gt;/data/sdm/crbnk/in/incoming&lt;/value&gt;</p>
<p>&lt;/property&gt;</p></td>
</tr>
</tbody>
</table>

<table>
<thead>
<tr class="header">
<th>Parameter Name</th>
<th>File Archival Location</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Description</td>
<td>Archival location where the source files will be moved after processing(successful ingestion into HDP).</td>
</tr>
<tr class="even">
<td>Example</td>
<td>/data/sdm/crbnk/in/archive</td>
</tr>
<tr class="odd">
<td>Xml Tag</td>
<td>edmhdpif.config.source.nfs.archival.location</td>
</tr>
<tr class="even">
<td>Content from Parameter File</td>
<td><p>&lt;property&gt;</p>
<p>&lt;name&gt;edmhdpif.config.source.nfs.archival.location&lt;/name&gt;</p>
<p>&lt;value&gt;/data/sdm/crbnk/in/archive&lt;/value&gt;</p>
<p>&lt;/property&gt;</p></td>
</tr>
</tbody>
</table>

<table>
<thead>
<tr class="header">
<th>Parameter Name</th>
<th>Re-Run File Location</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Description</td>
<td>Location where the source files for re-run will be made available</td>
</tr>
<tr class="even">
<td>Example</td>
<td>/data/sdm/crbnk/in/rerun</td>
</tr>
<tr class="odd">
<td>Xml Tag</td>
<td>edmhdpif.config.source.nfs.rerun.location</td>
</tr>
<tr class="even">
<td>Content from Parameter File</td>
<td><p>&lt;property&gt;</p>
<p>&lt;name&gt;edmhdpif.config.source.nfs.rerun.location&lt;/name&gt;</p>
<p>&lt;value&gt;/data/sdm/crbnk/in/rerun&lt;/value&gt;</p>
<p>&lt;/property&gt;</p></td>
</tr>
</tbody>
</table>

<table>
<thead>
<tr class="header">
<th>Parameter Name</th>
<th>Rejected File Location</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Description</td>
<td>Rejected file location where the source files will be moved after processing.</td>
</tr>
<tr class="even">
<td>Example</td>
<td>/data/sdm/crbnk/in/rejected</td>
</tr>
<tr class="odd">
<td>Xml Tag</td>
<td>edmhdpif.config.source.nfs.rejected.location</td>
</tr>
<tr class="even">
<td>Content from Parameter File</td>
<td><p>&lt;property&gt;</p>
<p>&lt;name&gt;edmhdpif.config.source.nfs.rejected.location&lt;/name&gt;</p>
<p>&lt;value&gt;/data/sdm/crbnk/in/rejected&lt;/value&gt;</p>
<p>&lt;/property&gt;</p></td>
</tr>
</tbody>
</table>

<table>
<thead>
<tr class="header">
<th>Parameter Name</th>
<th>Error File Location</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Description</td>
<td>File location where the error files will be written during processing.</td>
</tr>
<tr class="even">
<td>Example</td>
<td>/data/sdm/crbnk/in/error</td>
</tr>
<tr class="odd">
<td>Xml Tag</td>
<td>edmhdpif.config.source.nfs.error.location</td>
</tr>
<tr class="even">
<td>Content from Parameter File</td>
<td><p>&lt;property&gt;</p>
<p>&lt;name&gt;edmhdpif.config.source.nfs.error.location&lt;/name&gt;</p>
<p>&lt;value&gt;/data/sdm/crbnk/in/error&lt;/value&gt;</p>
<p>&lt;/property&gt;</p></td>
</tr>
</tbody>
</table>

<table>
<thead>
<tr class="header">
<th>Parameter Name</th>
<th>Application Specific file location</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Description</td>
<td>File location where the application specific files will be written during processing.</td>
</tr>
<tr class="even">
<td>Example</td>
<td>/data/sdm/crbnk/in/appl</td>
</tr>
<tr class="odd">
<td>Xml Tag</td>
<td>edmhdpif.config.source.nfs.appl.location</td>
</tr>
<tr class="even">
<td>Content from Parameter File</td>
<td><p>&lt;property&gt;</p>
<p>&lt;name&gt;edmhdpif.config.source.nfs.appl.location&lt;/name&gt;</p>
<p>&lt;value&gt;/data/sdm/crbnk/in/appl&lt;/value&gt;</p>
<p>&lt;/property&gt;</p></td>
</tr>
</tbody>
</table>

<table>
<thead>
<tr class="header">
<th>Parameter Name</th>
<th>Journal Time Format</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Description</td>
<td>This is applicable for CDC systems, this indicates the time stamp format in the journal time column.</td>
</tr>
<tr class="even">
<td>Example</td>
<td>yyyy-mm-dd hh:mi:ss.ssssss</td>
</tr>
<tr class="odd">
<td>Xml Tag</td>
<td>edmhdpif.config.journaltime.format</td>
</tr>
<tr class="even">
<td>Content from Parameter File</td>
<td><p>&lt;property&gt;</p>
<p>&lt;name&gt; edmhdpif.config.journaltime.format &lt;/name&gt;</p>
<p>&lt;value&gt; yyyy-mm-dd hh:mi:ss.ssssss &lt;/value&gt;</p>
<p>&lt;/property&gt;</p></td>
</tr>
</tbody>
</table>

<table>
<thead>
<tr class="header">
<th>Parameter Name</th>
<th>EOD Marker Time Column</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Description</td>
<td>This is applicable for CDC systems; this indicates the column which contains the EOD time</td>
</tr>
<tr class="even">
<td>Example</td>
<td>MARKER_TIME</td>
</tr>
<tr class="odd">
<td>Xml Tag</td>
<td>edmhdpif.config.markertime.column</td>
</tr>
<tr class="even">
<td>Content from Parameter File</td>
<td><p>&lt;property&gt;</p>
<p>&lt;name&gt; edmhdpif.config.markertime.column &lt;/name&gt;</p>
<p>&lt;value&gt; MARKER_TIME&lt;/value&gt;</p>
<p>&lt;/property&gt;</p></td>
</tr>
</tbody>
</table>

<table>
<thead>
<tr class="header">
<th>Parameter Name</th>
<th>EOD Date Column</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Description</td>
<td>This is applicable for CDC systems; this indicates the column which contains the EOD Date</td>
</tr>
<tr class="even">
<td>Example</td>
<td>EOD_DATE</td>
</tr>
<tr class="odd">
<td>Xml Tag</td>
<td>edmhdpif.config.eoddate.column</td>
</tr>
<tr class="even">
<td>Content from Parameter File</td>
<td><p>&lt;property&gt;</p>
<p>&lt;name&gt; edmhdpif.config.eoddate.column &lt;/name&gt;</p>
<p>&lt;value&gt; EOD_DATE&lt;/value&gt;</p>
<p>&lt;/property&gt;</p></td>
</tr>
</tbody>
</table>

<table>
<thead>
<tr class="header">
<th>Parameter Name</th>
<th>Batch File Record Type Column</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Description</td>
<td>Y / N – Y– means the data has a column which has Activity type as indicator like Insert, Update, Delete. The details of which column has this value has to be defined on table config template, N – means the data does not have such indicator.</td>
</tr>
<tr class="even">
<td>Example</td>
<td>Yes</td>
</tr>
<tr class="odd">
<td>Xml Tag</td>
<td>edmhdpif.config.batch.recordtype</td>
</tr>
<tr class="even">
<td>Content from Parameter File</td>
<td><p>&lt;property&gt;</p>
<p>&lt;name&gt; edmhdpif.config.batch.recordtype &lt;/name&gt;</p>
<p>&lt;value&gt; Y&lt;/value&gt;</p>
<p>&lt;/property&gt;</p></td>
</tr>
</tbody>
</table>

<table>
<thead>
<tr class="header">
<th>Parameter Name</th>
<th>Row History Schema</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Description</td>
<td>The structure of the row history table which will be created on hive. Row history table has the file name to rowid of the data.</td>
</tr>
<tr class="even">
<td>Example</td>
<td>rowid VARCHAR(100) ^filename VARCHAR(1000)</td>
</tr>
<tr class="odd">
<td>Xml Tag</td>
<td>edmhdpif.config.rowhistory.schema</td>
</tr>
<tr class="even">
<td>Content from Parameter File</td>
<td><p>&lt;property&gt;</p>
<p>    &lt;name&gt;edmhdpif.config.rowhistory.schema&lt;/name&gt;</p>
<p>    &lt;value&gt;rowid VARCHAR(100) ^filename VARCHAR(1000)&lt;/value&gt;</p>
<p>&lt;/property&gt;</p></td>
</tr>
</tbody>
</table>

<table>
<thead>
<tr class="header">
<th>Parameter Name</th>
<th>Timestamp Column</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Description</td>
<td>Applicable for CDC based sourcing, the column name specified for the first 1st columns which is a timestamp. CDC populated the column with the activity time from the database.</td>
</tr>
<tr class="even">
<td>Example</td>
<td>c_journaltime</td>
</tr>
<tr class="odd">
<td>Xml Tag</td>
<td>edmhdpif.config.timestamp.column</td>
</tr>
<tr class="even">
<td>Content from Parameter File</td>
<td><p>&lt;property&gt;</p>
<p>    &lt;name&gt;edmhdpif.config.timestamp.column&lt;/name&gt;</p>
<p>    &lt;value&gt; c_journaltime &lt;/value&gt;</p>
<p>&lt;/property&gt;</p></td>
</tr>
</tbody>
</table>

<table>
<thead>
<tr class="header">
<th>Parameter Name</th>
<th>Timestamp Column Format</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Description</td>
<td>Applicable for CDC based sourcing, the column name specified for the first 1st columns which is a timestamp. The format of the timestamp field.</td>
</tr>
<tr class="even">
<td>Example</td>
<td>yyyy-mm-dd hh:mi:ss.ssssss</td>
</tr>
<tr class="odd">
<td>Xml Tag</td>
<td>edmhdpif.config.timestamp.column.format</td>
</tr>
<tr class="even">
<td>Content from Parameter File</td>
<td><p>&lt;property&gt;</p>
<p>    &lt;name&gt;edmhdpif.config.timestamp.column.format &lt;/name&gt;</p>
<p>    &lt;value&gt; yyyy-mm-dd hh:mi:ss.ssssss&lt;/value&gt;</p>
<p>&lt;/property&gt;</p></td>
</tr>
</tbody>
</table>

<table>
<thead>
<tr class="header">
<th>Parameter Name</th>
<th>Date Column Format</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Description</td>
<td>The format in which the data columns need to be maintained in storage and processed area.</td>
</tr>
<tr class="even">
<td>Example</td>
<td>yyyy-mm-dd</td>
</tr>
<tr class="odd">
<td>Xml Tag</td>
<td>edmhdpif.config.date.collumn.format</td>
</tr>
<tr class="even">
<td>Content from Parameter File</td>
<td><p>&lt;property&gt;</p>
<p>    &lt;name&gt;edmhdpif.config.date.column.format &lt;/name&gt;</p>
<p>    &lt;value&gt; yyyy-mm-dd&lt;/value&gt;</p>
<p>&lt;/property&gt;</p></td>
</tr>
</tbody>
</table>

<table>
<thead>
<tr class="header">
<th>Parameter Name</th>
<th>Time Zone</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Description</td>
<td>The time zone of the system generated time stamp, generally it is UTC.</td>
</tr>
<tr class="even">
<td>Example</td>
<td>UTC</td>
</tr>
<tr class="odd">
<td>Xml Tag</td>
<td>edmhdpif.config.timezone</td>
</tr>
<tr class="even">
<td>Content from Parameter File</td>
<td><p>&lt;property&gt;</p>
<p>    &lt;name&gt;edmhdpif.config.timezone&lt;/name&gt;</p>
<p>    &lt;value&gt;UTC&lt;/value&gt;</p>
<p>&lt;/property&gt;</p></td>
</tr>
</tbody>
</table>

<table>
<thead>
<tr class="header">
<th>Parameter Name</th>
<th>SRI Audit Schema</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Description</td>
<td>The set of columns which SDM adds to the data in the processed layer on to the open and nonopen dataset. – Should not be changed kept as parameter for future use.</td>
</tr>
<tr class="even">
<td>Example</td>
<td>start_date STRING NOT NULL ^start_time STRING NOT NULL ^end_date STRING NOT NULL ^end_time STRING NOT NULL ^del_flag STRING NOT NULL</td>
</tr>
<tr class="odd">
<td>Xml Tag</td>
<td>edmhdpif.config.sri.auditcolschema</td>
</tr>
<tr class="even">
<td>Content from Parameter File</td>
<td><p>&lt;property&gt;</p>
<p>        &lt;name&gt;edmhdpif.config.sri.auditcolschema&lt;/name&gt;</p>
<p>        &lt;value&gt;start_date STRING NOT NULL ^start_time STRING NOT NULL ^end_date STRING NOT NULL ^end_time STRING NOT NULL ^del_flag STRING NOT NULL&lt;/value&gt;</p>
<p>&lt;/property&gt;</p></td>
</tr>
</tbody>
</table>

<table>
<thead>
<tr class="header">
<th>Parameter Name</th>
<th>Verify Type Audit Schema</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Description</td>
<td>The set of columns which SDM adds to the data in the storage layer on to the verified dataset. – Should not be changed kept as parameter for future use.</td>
</tr>
<tr class="even">
<td>Example</td>
<td>rowId STRING NOT NULL ^filename STRING NOT NULL ^vds STRING NOT NULL</td>
</tr>
<tr class="odd">
<td>Xml Tag</td>
<td>edmhdpif.config.vtypes.auditcolschema</td>
</tr>
<tr class="even">
<td>Content from Parameter File</td>
<td><p>&lt;property&gt;</p>
<p>        &lt;name&gt;edmhdpif.config.vtypes.auditcolschema&lt;/name&gt;</p>
<p>        &lt;value&gt;rowId STRING NOT NULL ^filename STRING NOT NULL ^vds STRING NOT NULL&lt;/value&gt;</p>
<p>&lt;/property&gt;</p></td>
</tr>
</tbody>
</table>

<table>
<thead>
<tr class="header">
<th>Parameter Name</th>
<th>CDC based sourcing Audit Schema</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Description</td>
<td>The set of columns which SDM adds to the data in the while processing CDC generated files– Should not be changed kept as parameter for future use.</td>
</tr>
<tr class="even">
<td>Example</td>
<td>c_journaltime STRING NOT NULL ^c_transactionid STRING NOT NULL ^c_operationtype STRING NOT NULL ^c_userid STRING NOT NULL&lt;/value&gt;</td>
</tr>
<tr class="odd">
<td>Xml Tag</td>
<td>edmhdpif.config.system.auditcolschema</td>
</tr>
<tr class="even">
<td>Content from Parameter File</td>
<td><p>&lt;property&gt;</p>
<p>        &lt;name&gt;edmhdpif.config.system.auditcolschema&lt;/name&gt;</p>
<p>        &lt;value&gt;c_journaltime STRING NOT NULL ^c_transactionid STRING NOT NULL ^c_operationtype STRING NOT NULL ^c_userid STRING NOT NULL&lt;/value&gt;</p>
<p>&lt;/property&gt;</p></td>
</tr>
</tbody>
</table>

<table>
<thead>
<tr class="header">
<th>Parameter Name</th>
<th>Hive URL</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Description</td>
<td>Hive URL for Primary instance</td>
</tr>
<tr class="even">
<td>Example</td>
<td>jdbc://hive2://&lt;ipaddress/dns&gt;:&lt;port&gt;</td>
</tr>
<tr class="odd">
<td>Xml Tag</td>
<td>edmhdpif.config.hive.url</td>
</tr>
<tr class="even">
<td>Content from Parameter File</td>
<td><p>&lt;property&gt;</p>
<p>    &lt;name&gt; edmhdpif.config.hive.url &lt;/name&gt;</p>
<p>    &lt;value&gt; jdbc://hive2://namenode:10000&gt;&lt;/value&gt;</p>
<p>&lt;/property&gt;</p></td>
</tr>
</tbody>
</table>

<table>
<thead>
<tr class="header">
<th>Parameter Name</th>
<th>Hive User</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Description</td>
<td>User name for SDM to connect to Hive for creation of tables and addition of partitions.</td>
</tr>
<tr class="even">
<td>Example</td>
<td>user1</td>
</tr>
<tr class="odd">
<td>Xml Tag</td>
<td>edmhdpif.config.hive.user</td>
</tr>
<tr class="even">
<td>Content from Parameter File</td>
<td><p>&lt;property&gt;</p>
<p>    &lt;name&gt; edmhdpif.config.hive.url &lt;/name&gt;</p>
<p>    &lt;value&gt; user1&lt;/value&gt;</p>
<p>&lt;/property&gt;</p></td>
</tr>
</tbody>
</table>

<table>
<thead>
<tr class="header">
<th>Parameter Name</th>
<th>Hive Url secondary server</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Description</td>
<td>Hive URL for Primary instance</td>
</tr>
<tr class="even">
<td>Example</td>
<td>jdbc://hive2://&lt;ipaddress/dns&gt;:&lt;port&gt;</td>
</tr>
<tr class="odd">
<td>Xml Tag</td>
<td>edmhdpif.config.hive.dr.url</td>
</tr>
<tr class="even">
<td>Content from Parameter File</td>
<td><p>&lt;property&gt;</p>
<p>    &lt;name&gt; edmhdpif.config.hive.dr.url &lt;/name&gt;</p>
<p>    &lt;value&gt; jdbc://hive2://namenode:10000&gt;&lt;/value&gt;</p>
<p>&lt;/property&gt;</p></td>
</tr>
</tbody>
</table>

<table>
<thead>
<tr class="header">
<th>Parameter Name</th>
<th>Hive User secondary server</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Description</td>
<td>User name for SDM to connect to Hive for creation of tables and addition of partitions.</td>
</tr>
<tr class="even">
<td>Example</td>
<td>user1</td>
</tr>
<tr class="odd">
<td>Xml Tag</td>
<td>edmhdpif.config.hive.dr.user</td>
</tr>
<tr class="even">
<td>Content from Parameter File</td>
<td><p>&lt;property&gt;</p>
<p>    &lt;name&gt; edmhdpif.config.hive.dr.user &lt;/name&gt;</p>
<p>    &lt;value&gt; userdr1&lt;/value&gt;</p>
<p>&lt;/property&gt;</p></td>
</tr>
</tbody>
</table>

<table>
<thead>
<tr class="header">
<th>Parameter Name</th>
<th>Hive Config</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Description</td>
<td>Hive / Hadoop site xml path for Primary instance to be passed to Hive Connection Pool service</td>
</tr>
<tr class="even">
<td>Example</td>
<td>/etc/nifi/hdp_conf/hive-site.xml</td>
</tr>
<tr class="odd">
<td>Xml Tag</td>
<td>edmhdpif.config.hive.config.resources</td>
</tr>
<tr class="even">
<td>Content from Parameter File</td>
<td><p>&lt;property&gt;</p>
<p>   &lt;name&gt; edmhdpif.config.hive.config.resources &lt;/name&gt;</p>
<p>    &lt;value&gt; /etc/nifi/hdp_conf/hive-site.xml &lt;/value&gt;</p>
<p>&lt;/property&gt;</p></td>
</tr>
</tbody>
</table>

<table>
<thead>
<tr class="header">
<th>Parameter Name</th>
<th>Hive Config secondary</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Description</td>
<td>Hive / Hadoop site xml path for DR instance to be passed to Hive Connection Pool service</td>
</tr>
<tr class="even">
<td>Example</td>
<td>/etc/nifi/hdp_conf/hive-site.xml</td>
</tr>
<tr class="odd">
<td>Xml Tag</td>
<td>edmhdpif.config.hive.dr.config.resources</td>
</tr>
<tr class="even">
<td>Content from Parameter File</td>
<td><p>&lt;property&gt;</p>
<p>   &lt;name&gt; edmhdpif.config.hive.dr.config.resources &lt;/name&gt;</p>
<p>    &lt;value&gt; /etc/nifi/hdp_conf/hive-site.xml &lt;/value&gt;</p>
<p>&lt;/property&gt;</p></td>
</tr>
</tbody>
</table>

<table>
<thead>
<tr class="header">
<th>Parameter Name</th>
<th>Hadoop Config Resources</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Description</td>
<td>Hive / Hadoop site xml path for Primary instance to be passed to Put HDFS processor</td>
</tr>
<tr class="even">
<td>Example</td>
<td>/usr/hdp/current/hadoop/conf/hdfs-site.xml,/usr/hdp/current/hadoop/conf/core-site.xml</td>
</tr>
<tr class="odd">
<td>Xml Tag</td>
<td>edmhdpif.config.hadoop.config.resources</td>
</tr>
<tr class="even">
<td>Content from Parameter File</td>
<td><p>&lt;property&gt;</p>
<p>   &lt;name&gt; edmhdpif.config.hadoop.config.resources &lt;/name&gt;</p>
<p>    &lt;value&gt; /usr/hdp/current/hadoop/conf/hdfs-site.xml, /usr/hdp/current/hadoop/conf/core-site.xml &lt;/value&gt;</p>
<p>&lt;/property&gt;</p></td>
</tr>
</tbody>
</table>

<table>
<thead>
<tr class="header">
<th>Parameter Name</th>
<th>Additional Classpath</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Description</td>
<td>Additional classpath resources like wandisco path for Primary instance to be passed to Put HDFS processor</td>
</tr>
<tr class="even">
<td>Example</td>
<td>&lt;path&gt;</td>
</tr>
<tr class="odd">
<td>Xml Tag</td>
<td>edmhdpif.config.additional.classpath.resources</td>
</tr>
<tr class="even">
<td>Content from Parameter File</td>
<td><p>&lt;property&gt;</p>
<p>   &lt;name&gt; edmhdpif.config.additional.classpath.resources &lt;/name&gt;</p>
<p>    &lt;value&gt; &lt;path&gt; &lt;/value&gt;</p>
<p>&lt;/property&gt;</p></td>
</tr>
</tbody>
</table>


## Table Config<a name="Table-Config"></a>

 <table>
 <thead>
 <tr class="header">
 <th>Parameter Name</th>
 <th>Nature of the table</th>
 </tr>
 </thead>
 <tbody>
 <tr class="odd">
 <td>Description</td>
 <td>Nature of the table can be of two types, <p><strong>delta</strong> – data is going to be incremental in nature</p> <p><strong>txn</strong> – data is going to be transactional nature or snapshot in nature.</p></td>
 </tr>
 <tr class="even">
 <td>Example</td>
 <td>delta</td>
 </tr>
 <tr class="odd">
 <td>Xml Tag</td>
 <td><strong>sdm.table.crbnk_in_account.sourcetype</strong></td>
 </tr>
 <tr class="even">
 <td>Content from Parameter File</td>
 <td><p>&lt;property&gt;</p>
 <p>&lt;name&gt;sdm.table.crbnk_in_account.sourcetype&lt;/name&gt;</p>
 <p>&lt;value&gt;delta&lt;/value&gt;</p>
 <p>&lt;/property&gt;</p></td>
 </tr>
 </tbody>
 </table>

 <table>
 <thead>
 <tr class="header">
 <th>Parameter Name</th>
 <th>Primary Key of the table</th>
 </tr>
 </thead>
 <tbody>
 <tr class="odd">
 <td>Description</td>
 <td>It can be a single column or a set of columns.</td>
 </tr>
 <tr class="even">
 <td>Example</td>
 <td>accountno</td>
 </tr>
 <tr class="odd">
 <td>Xml Tag</td>
 <td><strong>sdm.table.crbnk_in_account.keycols</strong></td>
 </tr>
 <tr class="even">
 <td>Content from Parameter File</td>
 <td><p>&lt;property&gt;</p>
 <p>&lt;name&gt;sdm.table.crbnk_in_account.keycols&lt;/name&gt;</p>
 <p>&lt;value&gt;accountno&lt;/value&gt;</p>
 <p>&lt;/property&gt;</p></td>
 </tr>
 </tbody>
 </table>

 <table>
 <thead>
 <tr class="header">
 <th>Parameter Name</th>
 <th>Structure of the table</th>
 </tr>
 </thead>
 <tbody>
 <tr class="odd">
 <td>Description</td>
 <td>The structure of the table format “Column Name<strong>&lt;space&gt;</strong>Data Type([length],[scale])<strong>&lt;space&gt;</strong>NULL/NOT NULL<strong>&lt;space&gt;</strong>COMMENT ‘comments’<strong>&lt;space&gt;</strong>RULES rules<strong>^.</strong> The COMMENT and RULES are optional, the length and scale are applicable for numeric data type,</td>
 </tr>
 <tr class="even">
 <td>Example</td>
 <td>Accountno</td>
 </tr>
 <tr class="odd">
 <td>Xml Tag</td>
 <td><strong>sdm.table.crbnk_in_account. col_schema</strong></td>
 </tr>
 <tr class="even">
 <td>Content from Parameter File</td>
 <td><p>&lt;property&gt;</p>
 <p>&lt;name&gt;sdm.table.crbnk_in_account.col_schema&lt;/name&gt;</p>
 <p>&lt;value&gt;&lt;/value&gt;</p>
 <p>&lt;/property&gt;</p></td>
 </tr>
 </tbody>
 </table>

 <table>
 <thead>
 <tr class="header">
 <th>Parameter Name</th>
 <th>Header Record Marker</th>
 </tr>
 </thead>
 <tbody>
 <tr class="odd">
 <td>Description</td>
 <td>Value in the first column of the record which indicates the record is header or trailer or detail / data record. H- Header , D- Data and T- Trailer or 01-Header , 02- Details / /Data and 03 - Trailer</td>
 </tr>
 <tr class="even">
 <td>Example</td>
 <td>H</td>
 </tr>
 <tr class="odd">
 <td>Xml Tag</td>
 <td><strong>sdm.table.crbnk_in_account.headermarker</strong></td>
 </tr>
 <tr class="even">
 <td>Content from Parameter File</td>
 <td><p>&lt;property&gt;</p>
 <p>&lt;name&gt;sdm.table.crbnk_in_account.headermarker&lt;/name&gt;</p>
 <p>&lt;value&gt;H&lt;value/&gt;</p>
 <p>&lt;/property&gt;</p></td>
 </tr>
 </tbody>
 </table>

 <table>
 <thead>
 <tr class="header">
 <th>Parameter Name</th>
 <th>Trailer Record Marker</th>
 </tr>
 </thead>
 <tbody>
 <tr class="odd">
 <td>Description</td>
 <td>Value in the first column of the record which indicates the record is header or trailer or detail / data record. H- Header , D- Data and T- Trailer or 01-Header , 02- Details / /Data and 03 - Trailer</td>
 </tr>
 <tr class="even">
 <td>Example</td>
 <td>T</td>
 </tr>
 <tr class="odd">
 <td>Xml Tag</td>
 <td><strong>sdm.table.crbnk_in_account.trailermarker</strong></td>
 </tr>
 <tr class="even">
 <td>Content from Parameter File</td>
 <td><p>&lt;property&gt;</p>
 <p>&lt;name&gt;sdm.table.crbnk_in_account.trailermarker&lt;/name&gt;</p>
 <p>&lt;value&gt;T&lt;value/&gt;</p>
 <p>&lt;/property&gt;</p></td>
 </tr>
 </tbody>
 </table>

 <table>
 <thead>
 <tr class="header">
 <th>Parameter Name</th>
 <th>Data Record Marker</th>
 </tr>
 </thead>
 <tbody>
 <tr class="odd">
 <td>Description</td>
 <td>Value in the first column of the record which indicates the record is header or trailer or detail / data record. H- Header , D- Data and T- Trailer or 01-Header , 02- Details / /Data and 03 - Trailer</td>
 </tr>
 <tr class="even">
 <td>Example</td>
 <td>D</td>
 </tr>
 <tr class="odd">
 <td>Xml Tag</td>
 <td>sdm.table.crbnk_in_account.datamarker</td>
 </tr>
 <tr class="even">
 <td>Content from Parameter File</td>
 <td><p>&lt;property&gt;</p>
 <p>&lt;name&gt;sdm.table.crbnk_in_account.datamarker&lt;/name&gt;</p>
 <p>&lt;value&gt;D&lt;value/&gt;</p>
 <p>&lt;/property&gt;</p></td>
 </tr>
 </tbody>
 </table>

 <table>
 <thead>
 <tr class="header">
 <th>Parameter Name</th>
 <th>Header Record schema</th>
 </tr>
 </thead>
 <tbody>
 <tr class="odd">
 <td>Description</td>
 <td>The record structure of the header records, generally follows the same delimiter as the file.</td>
 </tr>
 <tr class="even">
 <td>Example</td>
 <td>headerindicator VARCHAR(1) ^country VARCHAR(2) ^business_date VARCHAR(20) ^run_date VARCHAR(20) ^sequence VARCHAR(1)</td>
 </tr>
 <tr class="odd">
 <td>Xml Tag</td>
 <td><strong>sdm.table.crbnk_in_account.headercolschema</strong></td>
 </tr>
 <tr class="even">
 <td>Content from Parameter File</td>
 <td><p>&lt;property&gt;</p>
 <p>&lt;name&gt;sdm.table.crbnk_in_account.headercolschema&lt;/name&gt;</p>
 <p>&lt;value&gt;headerindicator VARCHAR(1) ^country VARCHAR(2) ^business_date VARCHAR(20) ^run_date VARCHAR(20) ^sequence VARCHAR(1)&lt;/value&gt;</p>
 <p>&lt;/property&gt;</p></td>
 </tr>
 </tbody>
 </table>

 <table>
 <thead>
 <tr class="header">
 <th>Parameter Name</th>
 <th>Trailer Record schema</th>
 </tr>
 </thead>
 <tbody>
 <tr class="odd">
 <td>Description</td>
 <td>The record structure of the Trailer records, generally follows the same delimiter as the file.</td>
 </tr>
 <tr class="even">
 <td>Example</td>
 <td>trailerindicator VARCHAR(1) ^rowcount VARCHAR(15) ^dummy2 VARCHAR(15) ^dummy3 VARCHAR(15)</td>
 </tr>
 <tr class="odd">
 <td>Xml Tag</td>
 <td><strong>sdm.table.crbnk_in_account.trailercolschema</strong></td>
 </tr>
 <tr class="even">
 <td>Content from Parameter File</td>
 <td><p>&lt;property&gt;</p>
 <p>&lt;name&gt;sdm.table.crbnk_in_account.trailercolschema&lt;/name&gt;</p>
 <p>&lt;value&gt;trailerindicator VARCHAR(1) ^rowcount VARCHAR(15) ^dummy2 VARCHAR(15) ^dummy3 VARCHAR(15)&lt;/value&gt;</p>
 <p>&lt;/property&gt;</p></td>
 </tr>
 </tbody>
 </table>

 <table>
 <thead>
 <tr class="header">
 <th>Parameter Name</th>
 <th>Column Name of Operation type</th>
 </tr>
 </thead>
 <tbody>
 <tr class="odd">
 <td>Description</td>
 <td>The Column name in the file which has the operation type like I – Insert, D – Delete and B/A for Update.</td>
 </tr>
 <tr class="even">
 <td>Example</td>
 <td>RECTYPE</td>
 </tr>
 <tr class="odd">
 <td>Xml Tag</td>
 <td><strong>sdm.table.crbnk_in_account. operationtypecol</strong></td>
 </tr>
 <tr class="even">
 <td>Content from Parameter File</td>
 <td><p>&lt;property&gt;</p>
 <p>&lt;name&gt;sdm.table.crbnk_in_account.operationtypecol&lt;/name&gt;</p>
 <p>&lt;value&gt;RECTYPE&lt;/value&gt;</p>
 <p>&lt;/property&gt;</p></td>
 </tr>
 </tbody>
 </table>

 <table>
 <thead>
 <tr class="header">
 <th>Parameter Name</th>
 <th>Inserted data indicator</th>
 </tr>
 </thead>
 <tbody>
 <tr class="odd">
 <td>Description</td>
 <td>The value which indicates Insert data / new data in file</td>
 </tr>
 <tr class="even">
 <td>Example</td>
 <td>I</td>
 </tr>
 <tr class="odd">
 <td>Xml Tag</td>
 <td><strong>sdm.table.crbnk_in_account.insertvalue</strong></td>
 </tr>
 <tr class="even">
 <td>Content from Parameter File</td>
 <td><p>&lt;property&gt;</p>
 <p>&lt;name&gt;sdm.table.crbnk_in_account.insertvalue&lt;/name&gt;</p>
 <p>&lt;value&gt;I&lt;/value&gt;</p>
 <p>&lt;/property&gt;</p></td>
 </tr>
 </tbody>
 </table>

 <table>
 <thead>
 <tr class="header">
 <th>Parameter Name</th>
 <th>Deleted data indicator</th>
 </tr>
 </thead>
 <tbody>
 <tr class="odd">
 <td>Description</td>
 <td>The value which indicates deleted data record.</td>
 </tr>
 <tr class="even">
 <td>Example</td>
 <td>D</td>
 </tr>
 <tr class="odd">
 <td>Xml Tag</td>
 <td><strong>sdm.table.crbnk_in_account.deletevalue</strong></td>
 </tr>
 <tr class="even">
 <td>Content from Parameter File</td>
 <td><p>&lt;property&gt;</p>
 <p>&lt;name&gt;sdm.table.crbnk_in_account.deletevalue&lt;/name&gt;</p>
 <p>&lt;value&gt;D&lt;/value&gt;</p>
 <p>&lt;/property&gt;</p></td>
 </tr>
 </tbody>
 </table>

 <table>
 <thead>
 <tr class="header">
 <th>Parameter Name</th>
 <th>Before Image data indicator</th>
 <th></th>
 </tr>
 </thead>
 <tbody>
 <tr class="odd">
 <td>Description</td>
 <td>The value which indicates record which contain value before update operation on the source.</td>
 <td></td>
 </tr>
 <tr class="even">
 <td>Example</td>
 <td>B</td>
 <td></td>
 </tr>
 <tr class="odd">
 <td>Xml Tag</td>
 <td><strong>sdm.table.crbnk_in_account.beforevalue</strong></td>
 <td></td>
 </tr>
 <tr class="even">
 <td>Content from Parameter File</td>
 <td><p>&lt;property&gt;</p>
 <p>&lt;name&gt;sdm.table.crbnk_in_account.beforevalue&lt;/name&gt;</p>
 <p>&lt;value&gt;B&lt;/value&gt;</p>
 <p>&lt;/property&gt;</p></td>
 <td></td>
 </tr>
 </tbody>
 </table>

 <table>
 <thead>
 <tr class="header">
 <th>Parameter Name</th>
 <th>After Image data indicator</th>
 <th></th>
 </tr>
 </thead>
 <tbody>
 <tr class="odd">
 <td>Description</td>
 <td>The value which indicates record which contain value after update operation on the source.</td>
 <td></td>
 </tr>
 <tr class="even">
 <td>Example</td>
 <td>A</td>
 <td></td>
 </tr>
 <tr class="odd">
 <td>Xml Tag</td>
 <td><strong>sdm.table.crbnk_in_account.aftervalue</strong></td>
 <td></td>
 </tr>
 <tr class="even">
 <td>Content from Parameter File</td>
 <td><p>&lt;property&gt;</p>
 <p>&lt;name&gt;sdm.table.crbnk_in_account.aftervalue&lt;/name&gt;</p>
 <p>&lt;value&gt;B&lt;/value&gt;</p>
 <p>&lt;/property&gt;</p></td>
 <td></td>
 </tr>
 </tbody>
 </table>

# Nifi Template Components

### File Watcher

  - Waits for data in the configured incoming location.
  - supports expression based file patterns.
  - Picks up the file in the order of arrival.

### Fetch global parameters for current instance (Source + Country).

 The Stage pickups up the source country and other relevant parameters from the file name and converts as the flow file attribute.

### Check for Automated DDL aware indication

 For CDC based system or the source system has ability to provide the structure of the tables as schema files. The process help to check for the changes and redirects control to processor which changes the schema structures where ever required.

### Schema Evolution

 The Process identified the changed table and changes the table structure and existing data to accommodate the changes.

### Fetch Information from filename.

 The processor get the date and time from the filename and converts the same into a flow file attribute.

### Retrieve file structure from config.

 The processor fetches the schema structure of every file processed and updated the flow file attributes accordingly.

### Read File

 The Processor read the file and converts the same into a flow file.

### Unwanted Newline and unwanted character removal

 The processor removes unwanted characters from the files. The characters are “, \\ , \\n if additional characters need to be removed the processor can be changed.

### Capture record count

 The processor captures the record count of every file processed.

### File Validation

 File Validation has 3 different validations:
 1.  File row count with trailer row count.
 2.  File header validation
 3.  File Trailer Validation


# SDM enrichment

### Row-ID, File Name, Partition Name

The processor enriches the data with additional attributes like rowid, File name, Partition Name. Rowid is unique identifier generated for every record in the file and the rowid is sortable and when sorted it gives the order in which the data is received.

### Row History to lineage

 The processor records rowid and file mapping for lineage tracking into a table. Row History structure is as below.

 | Column Name | Datatype       | Description                                             |
 | ----------- | -------------- | ------------------------------------------------------- |
 | Rowid       | Varchar(20)    | Source name                                             |
 | Country     | Varchar(10)    | Country code                                            |
 | Tablename   | Varchar(100)   | Tablename for which invalid record has been identified  |
 | Data        | Varchar(20000) | The entire record from the file.                        |
 | Errormsg    | Varchar(2000)  | The details error message on the various data attribute |
 | Ts          | Varchar(20)    | Timestamp of processing                                 |

### Apply configured data transformations

 The processor applies the transformation specified on the table config xml over the data and record the transformation failures on to the separate store. Below is the table structure for transformation failures.

 | Column Name | Datatype       | Description                                             |
 | ----------- | -------------- | ------------------------------------------------------- |
 | Source      | Varchar(20)    | Source name                                             |
 | Country     | Varchar(10)    | Country code                                            |
 | Tablename   | Varchar(100)   | Tablename for which invalid record has been identified  |
 | Data        | Varchar(20000) | The entire record from the file.                        |
 | Errormsg    | Varchar(2000)  | The details error message on the various data attribute |
 | Ts          | Varchar(20)    | Timestamp of processing                                 |

### Structural validation of data

1.  Verified data
2.  Invalid data
3.  Warning due to defaulting

## EOD Processing

### EOD Indication check

### EOD Processing

### Recon

### File after EOD handling

### Operational data capture and logging

**Row count**
 1.  Landing count
 2.  Transform failure record count
 3.  Verified data record count
 4.  Invalid data record count
 5.  Warning due to defaulting count
 6.  Before Image Record Count
 7.  Duplicate record count
 8.  Sri open record count
 9.  Sri non-open record count
