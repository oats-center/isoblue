export const isoblueDataTree = {
  bookmarks: {
    _type: 'application/vnd.oada.bookmarks.1+json',
    _rev: 0,
    isoblue: {
      _type: 'application/vnd.oada.isoblue.1+json',
      _rev: 0,
      'device-index': {
        '*': {
          _type: 'application/vnd.oada.isoblue.device.1+json',
          _rev: 0,
          'trails': {
            _type: 'application/vnd.oada.trails.1+json',
            _rev: 0,
            'day-index': {
              '*': {
                _type: 'application/vnd.oada.trails.1+json',
                _rev: 0,
                'geohash-index': {
                  '*': {
                    _type: 'application/vnd.oada.trails.1+json',
                  },
                },
              },
            },
          },
        },
      },
    },
  },
};

