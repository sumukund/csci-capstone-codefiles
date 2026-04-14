########################################################################
#
# Copyright (c) 2022, STEREOLABS.
#
# All rights reserved.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
########################################################################
import triggered_audio
import json
import time
import mapping 
from collections import deque
def main():
    with open("triggered.json") as f:
        frames = json.load(f)

    FPS = 10
    velocity_history = deque(maxlen=100)
    dt = 1 / FPS
    current_time = 0
    engine = triggered_audio.AudioEngine()

    for frame in frames:
        print("FRAME:", frame["triggered"])
        velocity_history.append((frame['velocity'], current_time))
        acceleration = mapping.get_acceleration(velocity_history)
        print(acceleration)
        time.sleep(1 / FPS)
        current_time += dt

        engine.update(frame, acceleration)
if __name__ == "__main__":
    main()