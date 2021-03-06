global local_subnets: set[subnet] = { 192.168.1.0/24, 192.68.2.0/24, 172.16.0.0/20, 172.16.16.0/20, 172.16.32.0/20, 172.16.48.0/20 };
global my_count = 0;
global inside_networks: set[addr];
global outside_networks: set[addr];

event new_connection(c: connection)
    {
    ++my_count;
    if ( my_count <= 10 )
	{
        print fmt("The connection %s from %s on port %s to %s on port %s started at %s.", c$uid, c$id$orig_h, c$id$orig_p, c$id$resp_h, c$id$resp_p, strftime("%D %H:%M", c$start_time)); 
    }
    if ( c$id$orig_h in local_subnets)
    	{
	add inside_networks[c$id$orig_h];
        }
    else
        add outside_networks[c$id$orig_h];
	    
    if ( c$id$resp_h in local_subnets)
        {
        add inside_networks[c$id$resp_h];
        }
    else
        add outside_networks[c$id$resp_h];
    }

event connection_state_remove(c: connection)
    {
    if ( my_count <= 10 )
    	{
    	print fmt("Connection %s took %s seconds", c$uid, c$duration);	
    	}
    }

event zeek_done() 
    {
    print fmt("Saw %d new connections", my_count);
    print "These IPs are considered local";
    for (a in inside_networks)
        {
        print a;
        }
    print "These IPs are considered external";
    for (a in outside_networks)
        {
        print a;
        }
    }
