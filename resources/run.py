# Module for running processes with real time output
# Written by CorpNewt
# Source: https://github.com/corpnewt/pymodules/blob/884c3de15b6a2570afde52fe8a14a3e946ffb18a/run.py

import sys, subprocess, time, threading, shlex
try:
    from Queue import Queue, Empty
except:
    from queue import Queue, Empty

ON_POSIX = 'posix' in sys.builtin_module_names

class Run:

    def __init__(self):
        return

    def _read_output(self, pipe, q):
        try:
            for line in iter(lambda: pipe.read(1), b''):
                q.put(line)
        except ValueError:
            pass
        pipe.close()

    def _create_thread(self, output):
        # Creates a new queue and thread object to watch based on the output pipe sent
        q = Queue()
        t = threading.Thread(target=self._read_output, args=(output, q))
        t.daemon = True
        return (q,t)

    def _stream_output(self, comm, shell = False):
        output = error = ""
        p = None
        try:
            if shell and type(comm) is list:
                comm = " ".join(shlex.quote(x) for x in comm)
            if not shell and type(comm) is str:
                comm = shlex.split(comm)
            p = subprocess.Popen(comm, shell=shell, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0, universal_newlines=True, close_fds=ON_POSIX)
            # Setup the stdout thread/queue
            q,t   = self._create_thread(p.stdout)
            qe,te = self._create_thread(p.stderr)
            # Start both threads
            t.start()
            te.start()

            while True:
                c = z = ""
                try: c = q.get_nowait()
                except Empty: pass
                else:
                    sys.stdout.write(c)
                    output += c
                    sys.stdout.flush()
                try: z = qe.get_nowait()
                except Empty: pass
                else:
                    sys.stderr.write(z)
                    error += z
                    sys.stderr.flush()
                if not c==z=="": continue # Keep going until empty
                # No output - see if still running
                p.poll()
                if p.returncode != None:
                    # Subprocess ended
                    break
                # No output, but subprocess still running - stall for 20ms
                time.sleep(0.02)

            o, e = p.communicate()
            return (output+o, error+e, p.returncode)
        except:
            if p:
                try: o, e = p.communicate()
                except: o = e = ""
                return (output+o, error+e, p.returncode)
            return ("", "Command not found!", 1)

    def _decode(self, value, encoding="utf-8", errors="ignore"):
        # Helper method to only decode if bytes type
        if sys.version_info >= (3,0) and isinstance(value, bytes):
            return value.decode(encoding,errors)
        return value

    def _run_command(self, comm, shell = False):
        c = None
        try:
            if shell and type(comm) is list:
                comm = " ".join(shlex.quote(x) for x in comm)
            if not shell and type(comm) is str:
                comm = shlex.split(comm)
            p = subprocess.Popen(comm, shell=shell, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            c = p.communicate()
        except:
            if c == None:
                return ("", "Command not found!", 1)
        return (self._decode(c[0]), self._decode(c[1]), p.returncode)

    def run(self, command_list, leave_on_fail = False):
        # Command list should be an array of dicts
        if type(command_list) is dict:
            # We only have one command
            command_list = [command_list]
        output_list = []
        for comm in command_list:
            args   = comm.get("args",   [])
            shell  = comm.get("shell",  False)
            stream = comm.get("stream", False)
            sudo   = comm.get("sudo",   False)
            stdout = comm.get("stdout", False)
            stderr = comm.get("stderr", False)
            mess   = comm.get("message", None)
            show   = comm.get("show",   False)

            if not mess == None:
                print(mess)

            if not len(args):
                # nothing to process
                continue
            if sudo:
                # Check if we have sudo
                out = self._run_command(["which", "sudo"])
                if "sudo" in out[0]:
                    # Can sudo
                    if type(args) is list:
                        args.insert(0, out[0].replace("\n", "")) # add to start of list
                    elif type(args) is str:
                        args = out[0].replace("\n", "") + " " + args # add to start of string

            if show:
                print(" ".join(args))

            if stream:
                # Stream it!
                out = self._stream_output(args, shell)
            else:
                # Just run and gather output
                out = self._run_command(args, shell)
                if stdout and len(out[0]):
                    print(out[0])
                if stderr and len(out[1]):
                    print(out[1])
            # Append output
            output_list.append(out)
            # Check for errors
            if leave_on_fail and out[2] != 0:
                # Got an error - leave
                break
        if len(output_list) == 1:
            # We only ran one command - just return that output
            return output_list[0]
        return output_list