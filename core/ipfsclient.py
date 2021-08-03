import ipfshttpclient

class IpfsClient:
    def __init__(self):
        self.client = None

    def connect(self):
        """
        Connect to the IPFS daemon
        """
        try:
            self.client = ipfshttpclient.connect()
        except Exception as e:
            print("Error connecting to the client", e)  
	    
    def create_backup(self, file_path):
        """
        Add a file to the IPFS network
        :param path: Path of the file
        """
        node = self.client.add(file_path)
        return node

    def retrieve_backup(self, cid):
        """
        Add a file to the IPFS network
        :param cid: Content ID of the file
        """
        file = self.client.cat(cid)
        return file

    def close(self):
        """
        Close the connection to the IPFS daemon
        """
        try:
            self.client.close()
        except Exception as e:
            print("Error closing the client", e)   
    
    def get_id(self):
        """
        Get the ID of the current node
        """
        id = self.client.id()
        return id

    def list_keys(self):
        """
        Get a list of all the CIDs stored on the node
        """
        keys = self.client.pin.ls()
        return keys