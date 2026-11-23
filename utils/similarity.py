from sklearn.metrics.pairwise import cosine_similarity

def get_similarity(resume_vec, job_vec):
    return cosine_similarity(resume_vec, job_vec)[0][0]