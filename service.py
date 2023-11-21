import subprocess
import signal
import os
import time


def run_script(script_path):
    process = subprocess.Popen(["python3", script_path])
    return process


def start_service(N):
    try:
        print("\nSERVICE STARTED\n___")
        # Start the Proxy
        proxy = run_script("proxy/proxy.py")

        # Run N Server insatnces
        servers = []
        for _ in range(N):
            server = run_script("servers/server.py")
            time.sleep(1)
            servers.append(server)

        print("\nSERVICE READY\n___")

        # TERMINATE SERVICE
        input()
        print("\nSERVICE TERMINATED\n___")

    except KeyboardInterrupt:
        pass
    finally:
        # Terminate Proxy and Servers
        proxy.terminate()
        for server in servers:
            server.terminate()

        # Wait for Termination
        proxy.wait()
        for server in servers:
            server.wait()


if __name__ == "__main__":
    # Start the Service with N Servers
    start_service(N=5)
