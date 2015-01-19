import soundcloud
import settings_private
import operator


# create a client object with your app credentials


# find all sounds of buskers licensed under 'creative commons share alike'
#tracks =
#print map(lambda x: x.username, tracks)


tracks = client.get('/tracks', genres='punk', bpm={
    'from': 120
})
print tracks
print map(operator.attrgetter('title'), tracks)
# print tracks
