from wifi import Cell, Scheme

def connect(adapter, ssid, psk=None, quiet=False):
	if not quiet:
		print "***setting up wireless adapter***"
	signal = []

	# get a list of all the available SSIDs that match the arg ssid
	cells = Cell.where(adapter, lambda x: x.ssid == ssid)
	print cells
	if len(cells) == 0:
		if not quiet:
			print "Cannot find SSID:", ssid
		return False

	# find the SSID with the best signal strength and select it as the cell to connect to
	for c in cells:
		signal.append(c.signal)

	max_signal = max(signal)
	max_index = signal.index(max_signal)
	cell = cells[max_index]
	scheme = Scheme.for_cell(adapter, ssid, cell, passkey=psk)

	# overwrite the scheme if already in '/etc/network/interfaces'
	# save it to '/etc/network/interfaces' if not
	if Scheme.find(adapter, ssid):
		scheme.delete()
		scheme.save()
	else:
		scheme.save()

	# attempt to connect to ssid
	try:
		if not quiet:
			print 'connecting to SSID:', cell.ssid
		scheme.activate()
		if not quiet:
			print 'connection successful'
		return True
	except:
		if not quiet:
			print('connection failed')
		return False

def main():
	print connect('wlan0','MAN_CAVE',psk='6655752404', quiet=False)

if __name__ == "__main__":
	main()
