# Original Source Code: https://github.com/alumae/kaldi-gstreamer-server

__author__ = 'tanel and flier@techfak.uni-bielefeld.de'

# STD
import os
import sys
import json
import time
import Queue
import urllib
import argparse
import threading

# WS4PY
from ws4py.client.threadedclient import WebSocketClient

# ROS
import rospy


def rate_limited(maxPerSecond):
    minInterval = 1.0 / float(maxPerSecond)

    def decorate(func):
        lastTimeCalled = [0.0]

        def rate_limited_function(*args, **kargs):
            elapsed = time.clock() - lastTimeCalled[0]
            leftToWait = minInterval - elapsed
            if leftToWait > 0:
                time.sleep(leftToWait)
            ret = func(*args, **kargs)
            lastTimeCalled[0] = time.clock()
            return ret
        return rate_limited_function
    return decorate


class KaldiRosClient(WebSocketClient):
    def __init__(self, audiofile, url, protocols=None, extensions=None, heartbeat_freq=None, byterate=32000,
                 save_adaptation_state_filename=None, send_adaptation_state_filename=None):
        super(KaldiRosClient, self).__init__(url, protocols, extensions, heartbeat_freq)
        self.final_hyps = []
        self.audiofile = audiofile
        self.byterate = byterate
        self.final_hyp_queue = Queue.Queue()
        self.save_adaptation_state_filename = save_adaptation_state_filename
        self.send_adaptation_state_filename = send_adaptation_state_filename

    @rate_limited(30)
    def send_data(self, data):
        self.send(data, binary=True)

    def opened(self):
        rospy.loginfo(">>> Socket connection is open now")

        def send_data_to_ws():
            if self.send_adaptation_state_filename is not None:
                rospy.loginfo(">>> Sending adaptation state from %s" % self.send_adaptation_state_filename)
                try:
                    adaptation_state_props = json.load(open(self.send_adaptation_state_filename, "r"))
                    self.send(json.dumps(dict(adaptation_state=adaptation_state_props)))
                except:
                    e = sys.exc_info()[0]
                    rospy.logerr(">>> Failed to send adaptation state: %s", str(e))
            with self.audiofile as audiostream:
                for block in iter(lambda: audiostream.read(self.byterate / 4), ""):
                    self.send_data(block)
                    rospy.logdebug(">>> Audio sent, now sending EOS")
            self.send("EOS")

        t = threading.Thread(target=send_data_to_ws)
        t.start()

    def received_message(self, m):
        response = json.loads(str(m))
        if response['status'] == 0:
            if 'result' in response:
                trans = response['result']['hypotheses'][0]['transcript']
                if response['result']['final']:
                    # print >> sys.stderr, trans,
                    # self.final_hyps.append(trans)
                    rospy.loginfo(trans.replace("\n", "\\n"))
                else:
                    print_trans = trans.replace("\n", "\\n")
                    if len(print_trans) > 80:
                        print_trans = "... %s" % print_trans[-76:]
            if 'adaptation_state' in response:
                if self.save_adaptation_state_filename:
                    print >> sys.stderr, "Saving adaptation state to %s" % self.save_adaptation_state_filename
                    with open(self.save_adaptation_state_filename, "w") as f:
                        f.write(json.dumps(response['adaptation_state']))
        else:
            rospy.logerr("Received error from server (status %d)" % response['status'])
            if 'message' in response:
                rospy.logerr(">>> Error message:", response['message'])

    def get_full_hyp(self, timeout=60):
        return self.final_hyp_queue.get(timeout)

    def closed(self, code, reason=None):
        self.final_hyp_queue.put(" ".join(self.final_hyps))


def main():
    rospy.init_node('kaldi_ros')

    parser = argparse.ArgumentParser(description='Command line client for kaldigstserver')
    parser.add_argument('-u', '--uri', default="ws://localhost:8181/client/ws/speech", dest="uri",
                        help="Server websocket URI")
    parser.add_argument('-r', '--rate', default=32000, dest="rate", type=int,
                        help="Rate in bytes/sec at which audio should be sent to the server. NB! For raw 16-bit audio it must be 2*samplerate!")
    parser.add_argument('--save-adaptation-state', help="Save adaptation state to file")
    parser.add_argument('--send-adaptation-state', help="Send adaptation state from file")
    parser.add_argument('--content-type', default='',
                        help="Use the specified content type (empty by default, for raw files the default is  audio/x-raw, layout=(string)interleaved, rate=(int)<rate>, format=(string)S16LE, channels=(int)1")
    parser.add_argument('audiofile', help="Audio file to be sent to the server", type=argparse.FileType('rb'),
                        default=sys.stdin)
    args = parser.parse_args()

    content_type = args.content_type
    if content_type == '' and args.audiofile.name.endswith(".raw"):
        content_type = "audio/x-raw, layout=(string)interleaved, rate=(int)%d, format=(string)S16LE, channels=(int)1" % (
        args.rate / 2)

    ws = KaldiRosClient(args.audiofile, args.uri + '?%s' % (urllib.urlencode([("content-type", content_type)])),
                        byterate=args.rate,
                        save_adaptation_state_filename=args.save_adaptation_state,
                        send_adaptation_state_filename=args.send_adaptation_state)
    ws.connect()
    rospy.spin()

if __name__ == "__main__":
    main()
