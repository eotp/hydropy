# -*- coding: utf-8 -*-
"""
Created on Tue Oct 11 22:09:11 2016

@author: Marty
"""

from __future__ import absolute_import, print_function
import numpy as np
import pandas as pd

import hydropy as hp


class Station(object):
    """Holds data for a single stream gauge or precipitation gauge.

    TODO: Start simple. Create methods to populate the new Station with a
        dataframe, and a method to populate the new Station with data requested
        from a source. Later, add logic that allows these functions to be
        called from inside the __init__().

    Different types of data get held in different dataframes. Daily mean
    discharge is separated from 15 minute instantaneous data and peak
    instantaneous data. Each series can have derived series that share the same
    time index values in the same dataframe. For example, a daily mean
    discharge may also have an adjacent column for baseflow, quickflow, and
    daily total precipitation.

    Each station object can be created alone by passing a dataframe or by
    passing a site id and a data source at creation. However, new Stations will
    most often be created by an Analysis object.

    The Station class will have some methods associated with it for analysis
    and for saving.  Station.dmd.baseflow() will calculate baseflow for the
    daily mean discharge series; Station.iv.baseflow() will calculate baseflow
    for the instantaneous values.
    """

    def __init__(self, site, source=None, start=None, end=None, period=10):
        """Initialize the Station object by giving it an id that is derived
        from the id of the physical station site that is collecting the data.
        Save the **kwargs to the Station object.

        Example (future usage):
        -----------------------
        >>> newDF = pd.DataFrame(np.random.randn(10, 5))
        >>> newStation = hp.Station(newDF)

        >>> new_data = np.random.randn(10, 5)
        >>> newStation2 = hp.Station(new_data, columns=['a', 'b', 'c', 'd', 'e']))

        >>> newStation3 = hp.Station(['usgs01585200', 'usgs01581500'], source='usgs-dv')
        """
        # TODO: check if there is another object with the same site id.
        # TODO: check if there is any data for this site saved to disk.
        self.site = site
        
        if source is None:
            self.source = self._guess_the_source_from_site(site)
        else:
            self.source = source
        self.start = start
        self.end = end
        self.period = period
        #self.data is the default data to show for printing or other functions.
        self.data = None
        self.dailymean = None
        self.realtime = None
        self.type = None

        # future:
        # define these here.
        # self.site = site
        # self.source = source
        # self.start = start
        # self.end = end

        # future: pass the fetch function in at initialization.
        # if kwargs.get('fetch'):
        #    self.fetch = fetch
        # elif self.source == 'usgs-iv':
        #    self.fetch = get_usgs(self.site, 'iv', self.start, self.end)
        # elfi self.source == 'usgs-dv':
        #    self.fetch = get_usgs(self.site, 'dv', self.start, self.end)
        # elif self.source is None:
        #   print('Must set source')
        # else:
        #   raise HydroNameError('The source {0} is not defined.'
        #                        .format(source))
        #
        # self.data = self.fetch()

    def _guess_the_source_from_site(self, sitename):
        if sitename[0:4] == 'usgs':
            guess = 'usgs-dv'
        elif sitename[:-1] == 'L':
            guess = 'vmm'
        else:
            # I don't know what this is.
            guess = None
        return guess
    """
    def __str__(self):
        return str(self.data)

    def __repr__(self):
        return repr(self.data)

    def _repr_html_(self):
    #    """  # return the data formatted as html in an IPython notebook.
    #    """
    #    if self.data is None:
    #        return "No data for this Station"
    #    return pd.DataFrame._repr_html_(self.data.data)
    # """
    def fetch(self, source=None, start=None, end=None,
              period=1, **kwargs):
        """Retrieve data from a source.

        For now, use source as a switch to call a retrieval function. In the
        future, maybe set the fetch function when the object is initialized and
        then call it.

        Arguments:
        ---------
            source ('usgs-iv' | 'usgs-dv'): the data source.

            start (date str): a string to represent the start date. Right now,
                this is just a string that gets passed to the usgs. It should
                take on the form 'yyyy-mm-dd'.

            end (date str): a string to represent the end date. It should
                take on the form 'yyyy-mm-dd'

            period (int): number of days in the past to request data. Not
                implemented yet.

        Returns:
        -------
            self

        Raises:
        ------
            HydroSourceError: when a source that has not been implemented is
                requested.

        Example:
        -------

        >>> HerringRun = Station('01585200')
        >>> HerringRun.fetch()

        Fetches the past 1 day of values.

        >>> StonyRun = Station('01589464')
        >>> StonyRun.fetch(source='usgs-iv', start='2014-06-01',
                           end='2014-06-04')

        Fetches instantaneous values with a collection interval of 15 minutes
        for June 1-4, 2014.
        """
        # Update the dates if they haven't already been set.
        # TODO: check if the new fetch dates extend the record.
        # Does the new period cover more recent time than self.end?
        # Does the new period reach back earlier than self.start?
        # Is the new end more recent than self.end?
        # Is the new start earlier than self.start?
        #
        # For now, change the dates if they are included.
        if start is not None:
            self.start = start
        if end is not None:
            self.end = end
        if period is not None:
            self.period = period

        if source is None:
            if self.source is None:
                raise hp.HydroSourceError("No source was defined for this "
                                          ".fetch() request. To set a source, "
                                          "use .fetch(source='usgs-iv') or "
                                          "another source, such as 'usgs-dv'.")
            else:
                source = self.source
        if source == 'usgs-dv':
            # retrieve usgs data. Save to dailymean as a HydroAnalysis object.
            usgs_id = self.site[4:]
            df = hp.get_usgs(usgs_id, 'dv', self.start, self.end)
            self.dailymean = hp.HydroAnalysis(df)
            self.type = 'dailymean'
            self.data = self.dailymean
            self.source = source
        elif source == 'usgs-iv':
            # retrieve usgs iv data. Save to realtime.
            usgs_id = self.site[4:]
            df = hp.get_usgs(usgs_id, 'iv', self.start, self.end)
            self.realtime = hp.HydroAnalysis(df)
            self.type = 'realtime'
            self.data = self.realtime
            self.source = source
        else:
            raise hp.HydroSourceError('The source {0} is not defined.'
                                      .format(source))

        return self

    def pandas(self, data, **kwargs):
        """Create a station object using the pandas constructor.

                 data=None, # create a dataframe through Pandas.
                 index=None, # Pandas uses this to create a dataframe.
                 site=None, # use to identify this Station.
                 source=None, # Needed to collect data
                 start=None,
                 end=None,
                 period=None,
                 **kwargs):
        Initialize a new Station object.

        You can create a new station by passing in a new dataframe or by
        specifying the source and site id.
        """

        # if data is None,
        if data is None:
            # use the other arguments to retrieve data from a source.
            pass
        if isinstance(data, pd.DataFrame):
            # they sent us a dataframe. I guess there ain't much to do...?
            # or send this dataframe to pandas.dataframe constructor.
            pass
        else:
            # Send data to Pandas; maybe it will create a dataframe for us.
            # try:  #Maybe don't catch this error? is the message good enough?
            # Pandas accepts
            pass


class Analysis(object):
    """holds data for multiple Stations.
    """

    def __init__(self, data, source=None, start=None,
                 end=None, period=None, **kwargs):
        """
        Initialize with a list of sites and their source, or a dataframe.

        Arguments
        ---------
            data: a list of site ids
            source: ('usgs-iv' | 'usgs-dv') the data source.

        Returns
        -------
            self

        Raises
        ------
            HydroSourceError: when a source that has not been implemented is
                requested.

        Example
        -------
        Create a new Analysis object by passing a list of sites and a source:

        >>> my_study = hp.Analysis(['01585200', '01582500'], source='usgs-dv')

        Create a new Analysis object by passing a list of dictionaries that
        specify the site id and the data source:

        >>> sites = [{site: '01585200', source: 'usgs-dv'},
                     {site: '01582500', source: 'usgs-iv'}]
        >>> study2 = hp.Analysis(sites)

        """
        self.station_list = []
        self.df_dict = {}
        self.panel = None
        self.start = start
        self.end = end
        self.period = period

        if isinstance(data, pd.Panel):
            # TODO: Creating an Analysis object directly from a panel will
            # cause some problems later on. Normally, an Analysis object should
            # be created out of Station objects, which will handle saving data
            # and handling metadata. This bypasses that functionality, so how
            # will that functionality be included?
            self.create_panel(data)
            self.stations = list(self.panel.items)
            if source is None:
                print("please set the source for the dataset.")
        elif isinstance(data, list) and source is not None:
            if source == 'usgs-dv' or source == 'usgs-iv':
                for site in data:
                    new_station = hp.Station(site, source=source).fetch()
                    self.df_dict[site] = new_station.data.data
                    # call new_station.fetch(site, source, start=start, end=end)
                    self.station_list.append(new_station)
                self.create_panel(self.df_dict)
            else:
                # Raise an error if an unknown source is given.
                raise hp.HydroSourceError("The {0} service is not implemented"
                                          "yet.".format(source))
        # Phase 2: dealing with a dictionary as input.
        elif isinstance(data, dict):
            self.source = 'dict'

    def create_panel(self, data):
        """create a panel from a dictionary of dataframes.

        arguments:
        ---------
            data (pd.Panel): a pandas Panel, with each station as an item
                holding a dataframe.
            data (dict): a dict that uses the site_id as the key, and the
                dataframe from that station as the value.
        returns:
        -------
            self
        """
        if isinstance(data, pd.Panel):
            self.panel = data
        elif isinstance(data, dict):
            self.panel = pd.Panel(data)
        else:
            raise hp.HydroTypeError("Data of type {0} was supplied to a method"
                                 " that only accepts type pd.Dataframe or dict"
                                 .format(type(data)))
        return self
