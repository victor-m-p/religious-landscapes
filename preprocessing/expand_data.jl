using Printf, Statistics, Distributions, DelimitedFiles, CSV, DataFrames, IterTools

# loads 
dir = @__DIR__
path_configuration_probabilities = replace(dir, "preprocessing" => "data/preprocessing/configuration_probabilities.txt")
path_configurations = replace(dir, "preprocessing" => "data/preprocessing/configurations.txt")
path_flattened = replace(dir, "preprocessing" => "data/preprocessing/data_flattened.csv")

# setup
n_nodes, maxna = 20, 5

# read stuff
p = readdlm(path_configuration_probabilities) 
configurations = readdlm(path_configurations)
data_flattened = DataFrame(CSV.File(path_flattened))
mat_flattened = Matrix(data_flattened)

# quick functions
f(iterators...) = vec([collect(x) for x in product(iterators...)])
matchrow(a,B) = findfirst(i->all(j->a[j] == B[i,j],1:size(B,2)),1:size(B,1))

## expand nan
function expand_nan(l)
    lc = [x == 0 ? [1, -1] : [x] for x in l]
    return return f(lc...)
end 

## main function
function get_ind(data_state, configurations, n_nodes)
    v_ind = Vector{Int64}(undef, 0)
    m_obs = Matrix{Int64}(undef, 0, n_nodes)
    for i in data_state
        m = reshape(i, 1, length(i))
        hit = matchrow(m, configurations)
        v_ind = [v_ind;hit]
        m_obs = [m_obs;m]
    end 
    return v_ind, m_obs
end 

## the major loop
rows, cols = size(mat_flattened)
total_states = Matrix{Int64}(undef, 0, n_nodes)
total_praw = Vector{Float64}(undef, 0)
total_pnorm = Vector{Float64}(undef, 0)
total_entry = Vector{Int64}(undef, 0)
total_pind = Vector{Int64}(undef, 0)
for i in [1:1:rows;] 
    println(i)
    entry_id = mat_flattened[i,1]
    vals = mat_flattened[i:i, 2:cols] # uhhh...?
    data_state = expand_nan(vals)
    p_index, obs_states = get_ind(data_state, configurations, n_nodes)
    p_raw = p[p_index]
    p_norm = p_raw./sum(p_raw, dims = 1)

    # tracking id 
    l = size(p_norm)[1]
    entry_vec = fill(entry_id, l)

    # append stuff
    global total_states = [total_states;obs_states]
    global total_praw = [total_praw;p_raw]
    global total_pnorm = [total_pnorm;p_norm] 
    global total_entry = [total_entry;entry_vec]
    global total_pind = [total_pind;p_index]
end

# final data  
mat = hcat(total_entry, total_states)
total_pind = total_pind .- 1 # for 0-indexing in python
d = DataFrame(
    entry_id = total_entry, # entry id 
    config_id = total_pind, # configuration id 
    config_prob = total_praw, # configuration probability 
    entry_prob = total_pnorm) # probability of being in this config for the entry id

# save stuff 
outfile_csv = replace(dir, "preprocessing" => "data/preprocessing/data_expanded.csv")
outfile_txt = replace(dir, "preprocessing" => "data/preprocessing/matrix_expanded.txt")
CSV.write(outfile_csv, d)
writedlm(outfile_txt, mat)